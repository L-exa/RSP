import socket
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import base64
import random
import time

class BeautifulChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Чат")
        self.root.geometry("860x640")
        self.root.configure(bg="#0d1117")
        self.root.resizable(False, False)

        # Сеть
        self.sock = None
        self.stop_event = threading.Event()
        self.queue = queue.Queue()
        self.my_name = None

        # Палитра
        self.bg = "#0d1117"
        self.fg = "#c9d1d9"
        self.accent = "#58a6ff"
        self.bubble_me_bg = "#1f6feb"
        self.bubble_other_bg = "#21262d"
        self.bubble_me_fg = "#ffffff"
        self.bubble_other_fg = "#c9d1d9"
        self.name_colors = [
            "#f85149","#da77f2","#ffa657","#ff7b72",
            "#79c0ff","#79e1b7","#d29922","#a5d6ff",
            "#ff7edb","#b7e1a1"
        ]

        self.build_ui()
        self.root.after(100, self.process_queue)

    # ---------- UI ----------

    def build_ui(self):
        # Верхняя панель
        top = tk.Frame(self.root, bg=self.bg)
        top.pack(fill=tk.X, padx=16, pady=12)

        left_title = tk.Label(top, text="💬 kipu.chat", bg=self.bg, fg=self.fg, font=("Segoe UI", 11, "bold"))
        left_title.pack(side=tk.LEFT)

        connect_frame = tk.Frame(top, bg=self.bg)
        connect_frame.pack(side=tk.RIGHT)

        entry_style = dict(font=("Segoe UI", 10), bg="#21262d", fg=self.fg, insertbackground=self.fg, relief=tk.FLAT)
        self.host_var = tk.StringVar(value="127.0.0.1")
        tk.Entry(connect_frame, textvariable=self.host_var, width=12, **entry_style).grid(row=0, column=0, padx=4)

        self.port_var = tk.StringVar(value="1503")
        tk.Entry(connect_frame, textvariable=self.port_var, width=6, **entry_style).grid(row=0, column=1, padx=4)

        self.name_var = tk.StringVar(value="enver")
        tk.Entry(connect_frame, textvariable=self.name_var, width=12, **entry_style).grid(row=0, column=2, padx=4)

        self.connect_btn = tk.Button(connect_frame, text="Подключиться", bg=self.accent, fg="white",
                                     relief=tk.FLAT, font=("Segoe UI", 10, "bold"), command=self.connect)
        self.connect_btn.grid(row=0, column=3, padx=6)

        # Основная область: скроллируемый список сообщений (Canvas + Frame)
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self.canvas = tk.Canvas(main, bg="#0d1117", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(main, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Контейнер сообщений внутри Canvas
        self.messages_frame = tk.Frame(self.canvas, bg=self.bg)
        self.messages_window = self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw", width=800)

        # Авто-размер canvas при изменении контента
        self.messages_frame.bind("<Configure>", self._on_frame_configure)

        # Нижняя панель ввода
        bottom = tk.Frame(self.root, bg="#161b22")
        bottom.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.msg_var = tk.StringVar()
        self.entry = tk.Entry(bottom, textvariable=self.msg_var, font=("Segoe UI", 11),
                              bg="#0d1117", fg="white", relief=tk.FLAT, insertbackground="white")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8, ipady=8)
        self.entry.bind("<Return>", lambda e: self.send_message())

        btn_frame = tk.Frame(bottom, bg="#161b22")
        btn_frame.pack(side=tk.RIGHT)

        self.file_btn = tk.Button(btn_frame, text="📎", font=("Segoe UI", 16), bg="#161b22", fg="#8b949e",
                                  relief=tk.FLAT, command=self.send_file)
        self.file_btn.pack(side=tk.LEFT, padx=6)

        self.send_btn = tk.Button(btn_frame, text="Отправить", bg=self.accent, fg="white", relief=tk.FLAT,
                                  font=("Segoe UI", 10, "bold"), command=self.send_message)
        self.send_btn.pack(side=tk.LEFT, padx=6)

    def _on_frame_configure(self, event):
        # Обновляем область прокрутки и ширину окна сообщений
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfigure(self.messages_window, width=self.canvas.winfo_width())

    # ---------- Цвет имени ----------

    def get_name_color(self, name):
        random.seed(name.lower())
        return random.choice(self.name_colors)

    # ---------- Добавление сообщения (Telegram стиль) ----------

    def add_message(self, sender, text, is_file=False, filename=None, filedata_b64=None):
        is_me = (sender == self.my_name)

        # Контейнер строки
        row = tk.Frame(self.messages_frame, bg=self.bg)
        row.pack(fill=tk.X, padx=8, pady=4, anchor="e" if is_me else "w")

        # Пузырёк
        bubble_bg = self.bubble_me_bg if is_me else self.bubble_other_bg
        bubble_fg = self.bubble_me_fg if is_me else self.bubble_other_fg

        bubble = tk.Frame(row, bg=bubble_bg)
        # Выравнивание: справа для меня, слева для других
        bubble.pack(side=tk.RIGHT if is_me else tk.LEFT, padx=6, pady=2)

        # Имя отправителя (только для чужих)
        if not is_me:
            name_color = self.get_name_color(sender)
            name_label = tk.Label(bubble, text=sender, bg=bubble_bg, fg=name_color, font=("Segoe UI", 9, "bold"))
            name_label.pack(anchor="w", padx=10, pady=(8, 2))

        # Текст/файл
        if not is_file:
            msg_label = tk.Label(bubble, text=text, bg=bubble_bg, fg=bubble_fg,
                                 font=("Segoe UI", 11), wraplength=520, justify="left")
            msg_label.pack(anchor="w", padx=10, pady=4)
        else:
            # Файловый пузырёк: имя файла + кнопка "Сохранить"
            file_top = tk.Frame(bubble, bg=bubble_bg)
            file_top.pack(anchor="w", padx=10, pady=(6, 2))
            file_icon = tk.Label(file_top, text="📄", bg=bubble_bg, fg=bubble_fg, font=("Segoe UI", 12))
            file_icon.pack(side=tk.LEFT, padx=(0, 6))
            file_name_label = tk.Label(file_top, text=filename, bg=bubble_bg, fg=bubble_fg,
                                       font=("Segoe UI", 11, "bold"))
            file_name_label.pack(side=tk.LEFT)

            btns = tk.Frame(bubble, bg=bubble_bg)
            btns.pack(anchor="w", padx=10, pady=(2, 8))
            save_btn = tk.Button(btns, text="Сохранить", bg="#30363d", fg=self.fg, relief=tk.FLAT,
                                 font=("Segoe UI", 9),
                                 command=lambda: self.save_received_file(filename, filedata_b64, sender))
            save_btn.pack(side=tk.LEFT)

        # Время
        ts = time.strftime("%H:%M")
        time_label = tk.Label(bubble, text=ts, bg=bubble_bg, fg="#9da3aa", font=("Segoe UI", 8))
        time_label.pack(anchor="e", padx=10, pady=(0, 8))

        # Прокрутка вниз
        self.canvas.yview_moveto(1.0)
        self.root.update_idletasks()

    def save_received_file(self, filename, b64data, sender):
        try:
            save = filedialog.asksaveasfilename(initialfile=filename, title=f"Сохранить файл от {sender}")
            if not save:
                return
            with open(save, "wb") as f:
                f.write(base64.b64decode(b64data))
            # Локальное уведомление
            self.add_message("Система", f"Файл {filename} сохранён.", is_file=False)
        except Exception as e:
            self.add_message("Система", f"Ошибка сохранения файла: {e}", is_file=False)

    # ---------- Сеть: подключение и приём ----------

    def connect(self):
        if self.sock:
            return
        try:
            host = (self.host_var.get().strip() or "127.0.0.1")
            port = int(self.port_var.get().strip() or "1503")
            name = (self.name_var.get().strip() or "User")
            if not name:
                messagebox.showwarning("Имя", "Введите имя!")
                return
            self.my_name = name

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.stop_event.clear()

            threading.Thread(target=self.receiver, daemon=True).start()

            self.connect_btn.config(text="Онлайн", bg="#238636")
            self.add_message("Система", f"Подключено к {host}:{port}", is_file=False)
        except Exception as e:
            self.sock = None
            messagebox.showerror("Ошибка", str(e))

    def receiver(self):
        buffer = ""
        while not self.stop_event.is_set():
            try:
                data = self.sock.recv(8192)
                if not data:
                    break
                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    self.queue.put(line)
            except Exception:
                break
        self.queue.put(None)

    def process_queue(self):
        while True:
            try:
                msg = self.queue.get_nowait()
            except queue.Empty:
                break

            if msg is None:
                self.add_message("Система", "Соединение потеряно.", is_file=False)
                try:
                    if self.sock:
                        self.sock.close()
                except:
                    pass
                self.sock = None
                self.connect_btn.config(text="Подключиться", bg=self.accent)
                break

            # Обработка: FILE:sender:filename:base64 | обычные: "name: text"
            if msg.startswith("FILE:"):
                try:
                    _, sender, filename, b64data = msg.split(":", 3)
                    self.add_message(sender.strip(), f"Файл: {filename.strip()}",
                                     is_file=True, filename=filename.strip(), filedata_b64=b64data)
                except Exception as e:
                    self.add_message("Система", f"Ошибка файла: {e}", is_file=False)
            else:
                if ":" in msg:
                    name, text = msg.split(":", 1)
                    self.add_message(name.strip(), text.strip(), is_file=False)
                else:
                    self.add_message("Система", msg, is_file=False)

        self.root.after(100, self.process_queue)

    # ---------- Отправка ----------

    def send_message(self):
        if not self.sock:
            return
        text = self.msg_var.get().strip()
        if not text:
            return
        msg = f"{self.my_name}: {text}\n"
        try:
            self.sock.sendall(msg.encode("utf-8"))
            self.msg_var.set("")
            # Не добавляем локально пузырёк, чтобы избежать дублей — сервер разошлёт всем, включая нас
        except Exception:
            self.add_message("Система", "Ошибка отправки сообщения.", is_file=False)

    def send_file(self):
        if not self.sock:
            return
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("utf-8")
            filename = os.path.basename(path)
            msg = f"FILE:{self.my_name}:{filename}:{b64}\n"
            self.sock.sendall(msg.encode("utf-8"))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ---------- Закрытие ----------

    def on_close(self):
        try:
            self.stop_event.set()
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    self.sock.close()
                except:
                    pass
        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BeautifulChat(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

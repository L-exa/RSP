# server.py — ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
import socket
import threading

HOST = "0.0.0.0"
PORT = 1503

clients = set()
clients_lock = threading.Lock()


def broadcast(data: bytes):
    """Отправляет данные ВСЕМ клиентам (включая отправителя)"""
    dead = []
    with clients_lock:
        for client in list(clients):
            try:
                client.sendall(data)
            except:
                dead.append(client)

    with clients_lock:
        for c in dead:
            clients.discard(c)
            try:
                c.close()
            except:
                pass


def handle_client(conn: socket.socket, addr):
    print(f"[+] Подключился {addr}")
    with clients_lock:
        clients.add(conn)

    buffer = b""  # Работаем с bytes — это надёжнее
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data

            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                if line.strip():
                    # Добавляем \n обратно и рассылаем всем
                    full_message = line + b'\n'
                    broadcast(full_message)
    except Exception as e:
        pass
    finally:
        with clients_lock:
            clients.discard(conn)
        print(f"[-] Отключился {addr}")
        conn.close()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Сервер запущен на {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
# Lab3ReentrantLock.py

import threading
import time
import sys

counter = 0
lock = threading.Lock()

ITERATIONS = 100_000

def increment_counter():
    global counter
    for _ in range(ITERATIONS):
        lock.acquire()
        try:
            temp = counter
            temp += 1
            counter = temp
        finally:
            lock.release()

def decrement_counter():
    global counter
    for _ in range(ITERATIONS):
        lock.acquire()
        try:
            temp = counter
            temp -= 1
            counter = temp
        finally:
            lock.release()

def main():

    p = int(input("Введите кол-во инкрементирующих потоков: "))
    m = int(input("Введите кол-во декрементирующих потоков: "))

    global counter
    counter = 0

    threads = []
    start_time = time.time()

    for _ in range(p):
        t = threading.Thread(target=increment_counter)
        threads.append(t)
        t.start()

    for _ in range(m):
        t = threading.Thread(target=decrement_counter)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    print(f"Общее время выполнения: {end_time - start_time:.4f} сек.")
    print(f"Финальное значение счётчика: {counter}")

if __name__ == "__main__":
    main()
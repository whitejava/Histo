def main():
    from threading import Lock
    lock = Lock()
    for _ in range(10):
        TestThread(lock).start()

from threading import Thread
class TestThread(Thread):
    def __init__(self, lock):
        Thread.__init__(self)
        self.lock = lock
    
    def run(self):
        while True:
            with self.lock:
                print('[')
                print(' ]')

if __name__ == '__main__':
    main()
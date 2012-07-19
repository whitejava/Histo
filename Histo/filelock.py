import threading
 
class host:
    def __init__(self):
        self._locks = dict()
        self._lock = threading.Lock()
    
    def acquire(self, path):
        with self._lock:
            if path not in self._lock:
                self._lock[path] = threading.Lock()
            self._locks[path].acquire()
    
    def release(self, path):
        with self._lock:
            self._locks[path].release()
            del self._locks[path]
            
hostinstance = host()

class filelock:
    def __init__(self, path):
        self._path = path
    
    def acquire(self):
        hostinstance.acquire(self._path)
    
    def release(self):
        hostinstance.acquire(self._path)
    
    def __enter__(self):
        self.acquire()
    
    def __exit(self,t,v,trace):
        self.release()
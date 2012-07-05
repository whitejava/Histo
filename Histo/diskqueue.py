import threading
import pickle
import os

class diskqueue:
    def __init__(self, file):
        self._file = file
        self._lock = threading.Lock()
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                self._queue = pickle.load(f)
        else:
            self._queue = []
            self._save()
    
    def empty(self):
        with self._lock:
            return self._queue == []
    
    def front(self):
        with self._lock:
            return self._queue[0]
    
    def append(self, x):
        with self._lock:
            for i in range(1, len(self._queue)):
                if self._queue[i] == x:
                    del self._queue[i]
                    break
            self._queue.append(x)
            self._save()
    
    def pop(self):
        with self._lock:
            del self._queue[0]
            self._save()
    
    def _save(self):
        with open(self._file, 'wb') as f:
            pickle.dump(self._queue, f)
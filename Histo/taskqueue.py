import threading
import pickle
import os

class NoTask(Exception):
    pass

class optimizedqueue:
    def __init__(self, base):
        self._base = base
        self._lock = threading.Lock()
    
    def empty(self):
        with self._lock:
            return self._base.empty()
    
    def getall(self):
        with self._lock:
            return self._base.getall()
        
    def append(self, x):
        with self._lock:
            q = self._base.getall()
            for i in range(len(q)):
                if q[i] == x:
                    self._base.removeat(i)
            self._base.append(x)

    def __getitem__(self, x):
        with self._lock:
            return self._base[x]

    def __delitem__(self, x):
        with self._lock:
            del self._base[x]
    
    def __len__(self):
        with self._lock:
            return len(self._base)
        
class taskqueue:
    def __init__(self, base):
        self._base = base
        self._lock = threading.Lock()
        self._fetched = []
    
    def empty(self):
        with self._lock:
            return self._base.empty()
    
    def append(self, x):
        with self._lock:
            return self._base.append(x)
    
    def fetchtask(self):
        with self._lock:
            for i in range(len(self._base)):
                if i not in self._fetched:
                    return (i, self._base[i])
            raise Exception('no task to fetch')
    
    def feedback(self, index, result = True):
        with self._lock:
            self._fetched.remove(index)
            if result:
                del self._base[index]

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
    
    def getall(self):
        with self._lock:
            return self._queue[:]
    
    def append(self, x):
        with self._lock:
            for i in range(1, len(self._queue)):
                if self._queue[i] == x:
                    del self._queue[i]
                    break
            self._queue.append(x)
            self._save()
    
    def __len__(self):
        with self._lock:
            return len(self._queue)
    
    def __getitem__(self, x):
        with self._lock:
            return self._queue[x]
    
    def __delitem__(self, x):
        with self._lock:
            del self._queue[x]
            self._save()
    
    def _save(self):
        dir = os.path.dirname(self._file)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(self._file, 'wb') as f:
            pickle.dump(self._queue, f)
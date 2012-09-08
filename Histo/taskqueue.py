import threading
import pickle
import os
import pclib

class notasksignal(Exception):
    pass

class taskqueue:
    def __init__(self, base):
        self.base = base
        self.fetchedtask = dict()
        self.lock = threading.Lock()
        self.availablecounter = pclib.limitedcounter()
    
    def append(self, x):
        with self.lock:
            self.base.append(x)
        self.availablecounter.increase()
    
    def fetchtask(self):
        self.availablecounter.decrease()
        with self.lock:
            fetchid = self.allocatefetchid()
            taskid, task = self.allocatetaskid()
            self.fetchedtask[fetchid] = taskid
            return fetchid, task
    
    def feedback(self, fetchid, result):
        with self.lock:
            assert type(result) is bool
            if result:
                self.finishtask(fetchid)
            else:
                self.restarttask(fetchid)
    
    def allocatefetchid(self):
        i = 0
        while True:
            if i not in self.fetchedtask:
                return i
            i += 1
    
    def allocatetaskid(self):
        allocatedtasks = self.fetchedtask.values()
        for i in range(len(self.base)):
            if i not in allocatedtasks:
                return i
        raise notasksignal()
    
    def finishtask(self,fetchid):
        taskid = self.fetchedtask[fetchid]
        for e in self.fetchedtask:
            assert self.fetchedtask[e] != taskid
            if self.fetchedtask[e] > taskid:
                self.fetchedtask[e] -= 1
        del self.fetchedtask[fetchid]
    
    def restarttask(self, fetchid):
        del self.fetchedtask[fetchid]
        self.availablecounter.increase()

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
    
    def append(self, x):
        with self._lock:
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
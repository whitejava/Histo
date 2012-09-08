import threading
import pickle
import os

class notasksignal(Exception):
    pass

class taskqueue:
    def __init__(self, base):
        self.base = base
        self.fetchedtask = dict()
        self.lock = threading.Lock()
        self.tasklock = threading.Lock()
    
    def append(self, x):
        with self.lock:
            self.base.append(x)
            self.onavailabletask()
    
    def fetchtask(self):
        self.waitforavailabletask()
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
        self.onavailabletask()
    
    def waitforavailabletask(self):
        self.tasklock.acquire()
    
    def onavailabletask(self):
        pass
    

class NoTask(Exception):
    pass

class taskqueue:
    def __init__(self, base):
        self._base = base
        self._lock = threading.Lock()
        self._fetched = dict()
    
    def empty(self):
        with self._lock:
            return self._base.empty()
    
    def __len__(self):
        with self._lock:
            return len(self._base)
    
    def append(self, x):
        with self._lock:
            for i in reversed(range(len(self._base))):
                if self._base[i] == x:
                    if not self._istaskfetched(i):
                        del self._base[i]
            return self._base.append(x)
    
    def fetchtask(self):
        with self._lock:
            fetchid = self._availablefetchid()
            taskid = self._availabletaskid()
            task = self._base[taskid]
            self._fetched[fetchid] = taskid
            return (fetchid, task)
    
    def _availabletaskid(self):
        for i in range(len(self._base)):
            if not self._istaskfetched(i):
                return i
        raise NoTask
    
    def _availablefetchid(self):
        for j in range(len(self._fetched)):
            if j not in self._fetched:
                return j
        return len(self._fetched)
    
    def _istaskfetched(self, taskid):
        return taskid in self._fetched.values()
    
    def feedback(self, fetchid, result = True):
        with self._lock:
            taskid = self._fetched[fetchid]
            del self._fetched[fetchid]
            if result:
                self._removetask(taskid)
    
    def _removetask(self, taskid):
        del self._base[taskid]
        for e in self._fetched:
            if self._fetched[e] >= taskid:
                self._fetched[e] -= 1

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
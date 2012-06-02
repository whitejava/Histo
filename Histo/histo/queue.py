class Postpone:
    def __init__(self,verb,interval=1.0):
        import threading
        self._verb = verb
        self._interval = interval
        self._lock = threading.Lock()
        self._need = False
        self._timer = self._new_timer()
    def start(self):
        with self._lock:
            self._need = True
            self._timer.cancel()
            self._timer = self._new_timer()
            self._timer.start()
    def at_once(self):
        with self._lock:
            self._timer.cancel()
            self._do_verb()
    def __enter__(self):
        return self
    def __exit__(self,t,v,trace):
        self.at_once()
    def _new_timer(self):
        import threading
        return threading.Timer(self._interval,self._lock_do_verb)
    def _do_verb(self):
        if self._need:
            self._verb()
            self._need = False
    def _lock_do_verb(self):
        with self._lock:
            self._do_verb()

class AutoSave:
    def __init__(self,obj,store):
        self._obj = obj
        self._store = store
    def __enter__(self):
        pass

class NotExist(Exception):
    pass

import histo.store
s = histo.store.PrintStorage()
try:
    q = s.load()
except NotExist:
    q = []
try:
    for i in range(10):
        q.append(i)
finally:
    s.save(q)
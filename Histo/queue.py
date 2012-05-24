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

class AutoSaveQueue:
    def __init__(self,storage):
        from threading import Lock
        self._storage = storage
        self._lock = Lock()
        self._auto_save = Postpone(self._save)
        if storage.exist():
            self._load()
        else:
            self._create()
            self._auto_save.start()
    def push(self,e):
        with self._lock:
            self._queue.append(e)
            self._auto_save.start()
    def pop(self):
        with self._lock:
            r = self._queue[0]
            del self._queue[0]
            self._auto_save.start()
            return r
    def __enter__(self):
        return self
    def __exit__(self,t,v,trace):
        self._auto_save.__exit__(t, v, trace)
    def _load(self):
        self._queue = self._storage.load()
    def _create(self):
        self._queue = []
    def _save(self):
        self._storage.save(self._queue)
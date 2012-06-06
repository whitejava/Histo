class writer:
    def __init__(self,files,part_size):
        self._files = files
        self._closed = False
        self._part_size = part_size
        if files.exists(0):
            self._load()
        else:
            self._create()
    
    def _write(self,b):
        if not b:
            return
        while len(self._cache) + len(b) >= self._part_size:
            cut = len(self._cache)+len(b) - self._part_size
            self._cache.extend(b[:cut])
            self._flush_cache()
            b = b[cut:]
        self._cache.extend(b)

    def __enter__(self):
        class c: pass
        r = c()
        r.write = self._write
        return r
    
    def __exit__(self,t,v,trace):
        if v == None:
            self._flush_cache()
            self._save_state()
    
    def _load(self):
        with self._files.open_for_read(0) as f:
            import pickle
            state = pickle.loads(f.read())
            self._file_size = state['file_size']
            self._cache = state['cache']
            if self._part_size != state['part_size']:
                raise IOError('part size not same')
    
    def _create(self):
        self._file_size = 0
        self._cache = bytearray()
        self._save_state()
    
    def _flush_cache(self):
        with self._files.open_for_write(1+self._file_size//self._part_size) as f:
            f.write(self._cache)
        self._cache = bytearray()
    
    def _save_state(self):
        with self._files.open_for_write(0) as f:
            import pickle
            d = {'file_size': self._file_size,
                 'part_size': self._part_size,
                 'cache': self._cache}
            f.write(pickle.dumps(d))
    
    def _ensure_not_closed(self):
        if self._closed:
            raise IOError('the writer is closed')
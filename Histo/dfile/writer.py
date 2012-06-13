class writer:
    def __init__(self, files, part_size):
        self._files = files
        self._part_size = part_size
        self._entered = False
        self._exited = False
        if files.exists(0):
            self._load()
        else:
            self._create()
    
    def write(self,b):
        self._ensure_in_with_block()
        if not b:
            return
        while len(self._cache) + len(b) >= self._part_size:
            p = self._cut(b, self._part_size - len(self._cache))
            self._cache.extend(p[0])
            self._write_cache()
            self._clear_cache()
            b = p[1]
            self._file_size += len(p[0])
        self._cache.extend(b)
        self._file_size += len(b)

    def get_file_size(self):
        self._ensure_in_with_block()
        return self._file_size

    def __enter__(self):
        if self._entered:
            raise IOError('enter twice is not allowed.')
        self._entered = True
        return self
    
    def __exit__(self,t,v,trace):
        self._exited = True
        if v == None:
            try: self._write_cache()
            except: pass
            else: self._save_state()
    
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
    
    def _clear_cache(self):
        self._cache = bytearray()
        
    def _write_cache(self):
        if self._cache:
            with self._files.open_for_write(1+self._file_size//self._part_size) as f:
                f.write(self._cache)
    
    def _save_state(self):
        with self._files.open_for_write(0) as f:
            import pickle
            d = {'file_size': self._file_size,
                 'part_size': self._part_size,
                 'cache': self._cache}
            f.write(pickle.dumps(d))
    
    def _ensure_in_with_block(self):
        if not self._entered or self._exited:
            raise IOError('state error')
    
    def _cut(self, b, n):
        return (b[:n],b[n:])
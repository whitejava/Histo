class reader:
    def __init__(self,files,part_size):
        self._files = files
        self._part_size = part_size
        self._entered = False
        self._exited = False
        self._pointer = 0
        self._part = None
        self._load()
    
    def read(self, size = None):
        self._ensure_in_with_block()
        if size == None or size > self._available():
            size = self._available()
        r = bytearray()
        while size:
            self._correct_part()
            part_remain = self._get_part_remain_size()
            read_size = min(size, part_remain)
            r.extend(self._read_part_fully(read_size))
            size -= read_size
            self._pointer += read_size
        return bytes(r)
    
    def seek(self, p):
        self._ensure_in_with_block()
        self._pointer = p
    
    def __enter__(self):
        self._entered = True
        return self
    
    def __exit__(self,*k):
        self._exited = True
        if self._part:
            self._close_part()
    
    def _load(self):
        with self._files.open_for_read(0) as f:
            import pickle
            state = pickle.loads(f.read())
            self._file_size = state['file_size']
            self._cache = state['cache']
            if self._part_size != state['part_size']:
                raise IOError('part size not same')
    
    def _available(self):
        return self._file_size - self._pointer
    
    def _correct_part(self):
        if not self._part:
            self._open_part()
        if not self._is_correct_part():
            self._close_part()
            self._open_part()
        if not self._is_correct_part_position():
            self._seek_part_to_correct_position()
    
    def _open_part(self):
        self._part_id = 1 + self._pointer//self._part_size
        self._part = self._files.open_for_read(self._part_id)
        self._part_position = 0
    
    def _is_correct_part(self):
        return self._part_id == 1 + self._pointer//self._part_size
    
    def _is_correct_part_position(self):
        return self._part_position == self._pointer % self._part_size
    
    def _read_part_fully(self, size = None):
        if size == None:
            size = self._get_part_remain_size()
        r = self._part.read(size)
        if len(r) != size:
            raise IOError('read length not enough')
        self._part_position += size
        return r
    
    def _close_part(self):
        self._part.close()
        
    def _ensure_in_with_block(self):
        if not self._entered or self._exited:
            raise IOError('not in with block')
        
    def _get_part_remain_size(self):
        return min(self._available(), self._part_size - self._pointer % self._part_size)
    
    def _seek_part_to_correct_position(self):
        self._part.seek(self._pointer%self._part_size)
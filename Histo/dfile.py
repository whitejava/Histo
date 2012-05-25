class DFileState:
    def _exist(self):
        import os
        return os.path.isfile(self._get_state_filename())
    
    def _load(self):
        fn = self._get_state_filename()
        with open(fn, 'r') as f:
            state = eval(f.readlines())
            if self._partition_size != state['partition_size']:
                raise IOError('Partition size is not same')
            self._length = state['length']
        self.seek_write(self._length)
        self.seek_read(0)
        
    def _create(self):
        self._length = 0;
        self._save()
        
    def _save(self):
        fn = self._get_state_filename()
        with open(fn, 'w') as f:
            state = {'partition_size': self._partition_size,
                     'length': self._length}
            f.write(repr(state))
            
    def _get_state_filename(self):
        import os
        return os.path.join(self._root, 'state')

def state_load_or_create(file):
    r = DFileState(file)
    if not r.exist():
        r.create()
    r.load()
    return r

def state_load(file):
    r = DFileState(file)
    r.load()
    return r

class DFileWriter:
    _1mb = 1*1024*1024
    _4digits_decimal = lambda x:str(x).zfill(4)
    def __init__(self, root, part_size = _1mb, idformat = _4digits_decimal):
        self._part = None
        self._root = root
        self._part_size = part_size
        self._idformat = idformat
        self._state_load_or_create()
        self._seek_end()
    
    def write(self, s):
        s = s[:]
        while s:
            write_size = self._get_part_remain_size()
            self._ensure_open_part()
            self._write_part(s[:write_size])
            self._pointer += write_size
            del s[:write_size]
        self._update_state()
    
    def seek(self, pos):
        self.close()
        self._pointer = pos
        self._open_part()
        self._seek_part()
        self._update_state()
    
    def tell(self):
        return self._pointer
    
    def flush(self):
        if self._part:
            self._part.flush()
    
    def close(self):
        if self._part:
            self._part.close()
            self._part = None
    
    def _state_load_or_create(self):
        s = DFileState(self._root)
        if not s.exist():
            s.create(self._part_size)
        s.load()
        self._state = s
    
    def _seek_end(self):
        self.seek(self._state.length)
    
    def _get_part_remain_size(self):
        return self._part_size - self._get_part_pos() 
    
    def _ensure_open_part(self):
        if self._worth_seek():
            self.seek(self._pointer)
            
    def _write_part(self, str):
        self._part.write(str)
    
    def _update_state(self):
        self._state.length = max(self._state.length, self._pointer)
    
    def _open_part(self):
        partid = self._get_part_id()
        self._part = open(self._get_part_file_name(partid), 'a')
        self._partid = partid
    
    def _seek_part(self):
        partpos = self._get_part_pos()
        self._part.seek(partpos)
        self._partpos = partpos
    
    def _get_part_pos(self):
        return self._pointer % self._part_size
    
    def _worth_seek(self):
        return self._partid != self._get_part_id() or self._partpos != self._get_part_pos()

    def _get_part_id(self):
        return self.pointer / self._part_size
    
    def _get_part_file_name(self, partid):
        import os
        return os.path.join(self._root, self._idformat(partid))
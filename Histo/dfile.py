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
    def __init__(self, root, partition_size = 1*1024*1024, idformat=lambda x:str(x).zfill(4)):
        self._root = root;
        self._idformat = idformat
        self._partition_size = partition_size
        self._writer = None
        self._lock()
        import os
        self._state = state_load_or_create(os.path.join(self._root, 'state'))
        
    def write(self, str):
        str = str[:]
        while str:
            self._ensure_writer()
            cur = self._pointer
            size = self._partition_size
            switch_point = (1 + cur/size)*size
            write_size = switch_point - cur
            self._writer.write(str[:write_size])
            self._pointer += write_size
            self._state.length = max(self._pointer, self._state_length)
            del str[:write_size]
    
    def _ensure_writer(self):
        if not self._writer or self._opened_part_id != self.pointer/self._partition_size:
            self.close()
            self._writer = self._open_cur_part()
            part_pos = self._pointer % self._partition_size
            self._writer.seek(part_pos)
    
    def _open_cur_part(self):
        import os
        part_id = self._pointer / self._partition_size
        cur = os.path.join(self._root, self._idformat(part_id))
        self._opened_part_id = part_id
        return open(cur,'a')
    
    def seek(self, pos):
        self._pointer = pos
        self.close()
        self._writer
    
    def tell(self):
        return self._pointer
    
    def flush(self):
        if self._writer:
            self._writer.flush()
    
    def close(self):
        if self._writer:
            self._writer.close()
            self._writer = None
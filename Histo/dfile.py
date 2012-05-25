class DFileState:
    def __init__(self, file, partsize):
        self._file = file
        self._partsize = partsize
    
    def exist(self):
        import os
        return os.path.exists(self._file)
    
    def create(self):
        self.length = 0
        self._modified = True
    
    def load(self):
        with open(self._file,'r') as f:
            d = f.readline()
            m = eval(d)
            self.length = m['length']
            if m['partsize'] != self._partsize:
                raise IOError('Part size is not same')
        self._modified = False
    
    def on_modify(self):
        self._modified = True
        
    def close(self):
        if self._modified:
            self._save()
    
    def _save(self):
        with open(self._file, 'w') as f:
            f.write(repr({'length': self.length,
                          'partsize': self._partsize}))
        self._modified = False

class DFileWriter:
    _1mb = 1*1024*1024
    _4digits_decimal = lambda x:str(x).zfill(4)
    def __init__(self, root, part_size = _1mb, idformat = _4digits_decimal):
        self._part = None
        self._partid = None
        self._partpos = None
        self._root = root
        self._create_root()
        self._part_size = part_size
        self._idformat = idformat
        self._modify = set()
        self._state_load_or_create()
    
    def write(self, s):
        while s:
            write_size = self._get_part_remain_size()
            self._ensure_open_part()
            write = s[:write_size]
            self._write_part(write)
            self._pointer += len(write)
            s = s[write_size:]
        self._update_state()
    
    def get_modify(self):
        return self._modify
    
    def seek(self, pos):
        self._close_part()
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
        self._close_part()
        self._state.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self,t,v,trace):
        self.close()
    
    def _close_part(self):
        if self._part:
            self._part.close()
            self._part = None
    
    def _state_load_or_create(self):
        s = DFileState(self._get_state_file_name(), self._part_size)
        if s.exist():
            s.load()
        else:
            s.create()
        self._pointer = s.length
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
        self._modify |= set([self._partid])
    
    def _update_state(self):
        self._state.length = max(self._state.length, self._pointer)
        self._state.on_modify()
    
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
        return self._pointer // self._part_size
    
    def _get_part_file_name(self, partid):
        import os
        return os.path.join(self._root, self._idformat(partid))
    
    def _get_state_file_name(self):
        import os
        return os.path.join(self._root, 'state')
    
    def _create_root(self):
        import os
        if not os.path.exists(self._root):
            os.makedirs(self._root)
            
def rand(len):
    import random
    return ''.join([''.join(random.sample('0123456789abcdef',1)) for i in range(len)])

def test():
    f = DFileWriter('D:\\dfile',10*1024*1024)
    s = rand(3**11)
    with f:
        for i in range(100):
            f.write(s)
    print(f.get_modify())
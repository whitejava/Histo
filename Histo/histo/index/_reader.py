from . import _format as format

class reader:
    def __init__(self,file):
        self._file = file
    
    def read(self):
        r = self._read_commit()
        if r == None:
            return None
        self._check_commit(r)
        return r
    
    def _read_commit(self):
        length = self._read_length()
        if length == None:
            return None
        data = self._read_data(length)
        return eval(str(data,'utf8'))
    
    def _check_commit(self,c):
        format.check(c)
    
    def _read_data(self,length):
        r = self._file.read(length)
        if len(r) != length:
            raise IOError('read length not enough')
        return r
    
    def _read_length(self):
        x = self._file.read(4)
        if not x:
            return None
        if len(x) != 4:
            raise IOError('length error')
        import struct
        return struct.unpack('!i', x)[0]
    
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        pass
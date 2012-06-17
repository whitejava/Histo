class writer:
    def __init__(self,out):
        self._out = out
    
    def write(self,commit):
        self._check_format(commit)
        self._out.write(self._tobytes(commit))
    
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        pass
    
    def _check_format(self,commit):
        from . import _format as format
        format.check(commit)
        
    def _tobytes(self,commit):
        data = bytes(repr(commit),'utf8')
        from struct import pack
        length = pack('!i',len(data))
        return length + data
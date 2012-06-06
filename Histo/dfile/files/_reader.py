try:
    from ..files._bytes_io.reader import reader as bytes_reader
except:
    from _bytes_io.reader import reader as bytes_reader

class reader:
    def __init__(self, bundle, n):
        self._buffer = bytes_reader(bundle.load(n))
        self._closed = False
    
    def read(self, size = None):
        self._ensure_not_closed()
        return self._buffer.read(size)
    
    def seek(self, pos):
        self._ensure_not_closed()
        return self._buffer.seek(pos)
    
    def close(self):
        self._ensure_not_closed()
        self._closed = True
        return self._buffer.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        self.close()
    
    def _ensure_not_closed(self):
        if self._closed:
            raise IOError('the reader is closed')
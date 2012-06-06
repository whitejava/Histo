from ._bytes_io.writer import writer as bytes_writer

class writer:
    def __init__(self, bundle, n):
        self._bundle = bundle
        self._n = n
        self._buffer = bytearray()
        self._bytes_writer = bytes_writer(self._buffer)
        self._closed = False
    
    def write(self, b):
        self._ensure_not_closed()
        self._bytes_writer.write(b)
    
    def close(self):
        self._ensure_not_closed()
        self._bundle.dump(self._n, self._buffer)
        self._bundle = None
        self._closed = True
    
    def _ensure_not_closed(self):
        if self._closed:
            raise IOError('writer is closed')
    
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        self.close()
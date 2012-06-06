from ._reader import reader
from ._writer import writer

class files:
    def __init__(self,bundle):
        self._bundle = bundle
    
    def open_for_write(self, n):
        return writer(self._bundle,n)
    
    def open_for_read(self, n):
        return reader(self._bundle,n)
    
    def exists(self, n):
        return self._bundle.exists(n)
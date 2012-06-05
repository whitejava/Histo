class reader:
    def __init__(self, data):
        self.data = bytes(data)
        self.pointer = 0
    
    def read(self, size = None):
        if size == None:
            size = self.available()
        r = self.data[self.pointer : self.pointer + size]
        self.pointer += len(r)
        return r
    
    def seek(self, pos):
        if pos > len(self.data):
            raise IOError('seek out of file')
        self.pointer = pos
    
    def available(self):
        return len(self.data) - self.pointer
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        self.close()
class writer:
    def __init__(self, data, n):
        self.data = data
        self.n = n
        
    def dump(self, b):
        self.data[self.n] = b
    
    def close(self):
        self.out = None
        
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        self.close()
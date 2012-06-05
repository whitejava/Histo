class writer:
    def __init__(self, out):
        self.out = out
        
    def write(self, b):
        self.out.extend(b)
    
    def close(self):
        self.out = None
        
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        self.close()
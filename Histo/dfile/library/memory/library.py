class library:
    def __init__(self):
        self.files = {}
    
    def dump(self,n,data):
        self.files[n] = data
    
    def load(self,n):
        return self.files[n]

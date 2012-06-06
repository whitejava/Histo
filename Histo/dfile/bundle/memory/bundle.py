class bundle:
    def __init__(self):
        self.files = {}
    
    def dump(self,n,data):
        self.files[n] = data
    
    def load(self,n):
        return self.files[n]
    
    def exists(self,n):
        for e in self.files.keys():
            if e == n:
                return True
        return False
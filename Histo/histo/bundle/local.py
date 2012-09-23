class Local:
    def __init__(self, root):
        self.root = root
        self.createIfNotExist()
    
    def open(self, name, mode):
        assert mode in ('wb', 'rb')
        return open(self.getFile(name), mode)
    
    def delete(self, name):
        import os
        os.unlink(self.getFile(name))
    
    def list(self):
        import os
        return os.listdir(self.root)
    
    def createIfNotExist(self):
        import os
        if not os.path.isdir(self.root):
            os.makedirs(self.root)
            
    def getFile(self, name):
        import os.path
        return os.path.join(self.root, name)
class Local:
    def __init__(self, root):
        self.root = root
        self.createIfNotExist()
    
    def open(self, name, mode):
        assert mode in 'wb', 'rb'
        import os.path
        return open(os.path.join(self.root, name), mode)
    
    def delete(self, name):
        import os
        os.unlink(name)
    
    def list(self):
        import os
        return os.listdir(self.root)
    
    def createIfNotExist(self):
        import os
        if not os.path.isdir(self.root):
            os.makedirs(self.root)
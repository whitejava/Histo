class Local:
    def __init__(self, root):
        self.root = root
        self.createIfNotExist()
        self.totalSize = sum(map(self.getSize, self.list()))
    
    def open(self, name, mode):
        assert mode in ('wb', 'rb')
        result = open(self.getFile(name), mode)
        if mode == 'wb':
            def increaseTotalSize(write0, data):
                result = write0(data)
                self.totalSize += len(data)
                return result
            from histo.bundle.filehook import FileHook
            result = FileHook(result, onWrite=increaseTotalSize)
        return result
    
    def delete(self, name):
        self.totalSize -= self.getSize(name)
        import os
        os.unlink(self.getFile(name))
    
    def list(self):
        import os
        return os.listdir(self.root)
    
    def exists(self, name):
        import os
        return os.path.isfile(self.getFile(name))
    
    def getSize(self, name):
        import os.path
        return os.path.getsize(self.getFile(name))
    
    def getTotalSize(self):
        return self.totalSize
    
    def createIfNotExist(self):
        import os
        if not os.path.isdir(self.root):
            os.makedirs(self.root)
            
    def getFile(self, name):
        import os.path
        return os.path.join(self.root, name)
class FileHook:
    def __init__(self, file, onClose = None):
        self.file = file
        self.onClose = self.denone(onClose)
    
    def read(self, limit):
        return self.file.read(limit)
    
    def write(self, data):
        return self.file.write(data)
    
    def close(self):
        self.onClose(self.file.close)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
    
    def denone(self, x):
        if x is None:
            def empty(*k):
                pass
            return empty
        else:
            return x
class FileHook:
    def __init__(self, file, onClose = None, onWrite = None):
        self.file = file
        self.onClose = denoneCallSelf(onClose)
        self.onWrite = denoneCallSelf(onWrite)
    
    def read(self, limit):
        return self.file.read(limit)
    
    def write(self, data):
        return self.onWrite(self.file.write, data)
    
    def close(self):
        self.onClose(self.file.close)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
    
def denoneCallSelf(x):
    if x is None:
        def callSelf(original, *k):
            return original(*k)
        return callSelf
    else:
        return x
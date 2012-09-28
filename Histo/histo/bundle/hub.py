class Hub:
    def __init__(self, bundles, volumes):
        self.bundles = bundles
        self.volumes = volumes
        self.state = self.getState()
        from threading import Lock
        self.lock = Lock()
        
    def open(self, name, mode):
        if mode == 'rb':
            return self.openForRead(name)
        elif mode == 'wb':
            return self.openForWrite(name)
        else:
            raise Exception('No such mode.')
    
    def delete(self, name):
        raise Exception('Not supported')
    
    def list(self):
        result = set()
        for e in self.bundles:
            result = result.union(e.list())
        return list(result)
    
    def exists(self, name):
        return any((e.exists(name) for e in self.bundles))
    
    def openForRead(self, name):
        bundle = self.findContainerBundle(name)
        return bundle.open(name, 'rb')
    
    def openForWrite(self, name):
        import io
        result = io.BytesIO()
        def onClose(close0):
            data = result.getvalue()
            close0()
            self.writeData(name, data)
        from .filehook import FileHook
        return FileHook(result, onClose=onClose)
    
    def findBigEnoughBundle(self, size):
        with self.lock:
            for i in range(len(self.bundles)):
                if self.getBundleRemainSize(i) >= size:
                    return i,self.bundles[i]
            raise Exception('Space not enough')
    
    def getBundleRemainSize(self, i):
        totalSize = self.volumes[i]
        usedSize = self.state['Usage'][i]
        return totalSize - usedSize
    
    def findContainerBundle(self, name):
        for e in self.bundles:
            if name in e.list():
                return e
        raise Exception('Container bundle not found.')
    
    def writeData(self, name, data):
        size = len(data)
        i,bundle = self.findBigEnoughBundle(size)
        with bundle.open(name, 'wb') as f:
            f.write(data)
        with self.lock:
            self.state['Usage'][i] += size
            
    def getUsageState(self):
        return [e.getTotalSize() for e in self.bundles]
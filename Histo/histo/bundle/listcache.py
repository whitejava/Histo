class ListCache:
    def __init__(self, bundle, cacheValidityDuration, exitSignal):
        self.bundle = bundle
        from histo.bundle.periodevent import PeriodEvent
        self.postUpdateCache = PeriodEvent(self.updateCache, cacheValidityDuration, exitSignal).set
        self.cache = []
    
    def open(self, name, mode):
        from histo.bundle.filehook import FileHook
        result = self.bundle.open(name, mode)
        def onClose(close0):
            close0()
            self.postUpdateCache()
        result = FileHook(result, onClose = onClose)
        return result
    
    def delete(self, name):
        return self.bundle.delete(name)
    
    def list(self):
        self.cache = self.bundle.list()
        return self.cache[:]
    
    def listWithCache(self):
        return self.cache[:]

    def updateCache(self):
        self.cache = self.bundle.list()
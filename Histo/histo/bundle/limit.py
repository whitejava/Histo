import logging
logger = logging.getLogger()

class Limit:
    def __init__(self, bundle, writeSpeed, readSpeed):
        self.bundle = bundle
        self.writeLimiter = Limiter(writeSpeed)
        self.readLimiter = Limiter(readSpeed)
    
    def open(self, name, mode):
        assert mode in ('rb', 'wb')
        f = self.bundle.open(name, mode)
        if mode == 'rb':
            return LimitReader(f, self.readLimiter)
        elif mode == 'wb':
            return LimitWriter(f, self.writeLimiter)
        else:
            raise Exception('No such mode.')
    
    def list(self):
        return self.bundle.list()
    
    def delete(self, name):
        return self.bundle.delete(name)

class Limiter:
    def __init__(self, maxSpeed):
        self.maxSpeed = maxSpeed
        self.maxInterval = 0.01
        self.currentSpeed = 0
        self.lastTime = 0
        from threading import Lock
        self.lock = Lock()
    
    def request(self, requestBytes):
        return Request(self, requestBytes)
    
    def requestBytes(self, limit):
        with self.lock:
            maxBytes = int(self.maxSpeed * self.maxInterval)
            if maxBytes == 0:
                maxBytes = 1
            bytes2 = min(limit, maxBytes)
            sleep = bytes2 / self.maxSpeed
            import time
            time.sleep(sleep)
            return bytes2
    
    def success(self, size):
        pass

class Request:
    def __init__(self, limiter, requestBytes):
        self.limiter = limiter
        self.requestBytes = requestBytes
        self.successBytes = 0
    
    def __iter__(self):
        return self.Iterator()
    
    def success(self, size):
        self.successBytes += size
        self.limiter.success(size)
    
    def Iterator(self):
        while True:
            remainBytes = self.requestBytes - self.successBytes
            if remainBytes <= 0:
                break
            requestBytes = self.limiter.requestBytes(remainBytes)
            yield requestBytes
            remainBytes -= requestBytes

class LimitReader:
    def __init__(self, file, limiter):
        self.file = file
        self.limiter = limiter
    
    def read(self, limit):
        import io
        result = io.BytesIO()
        request = self.limiter.request(limit)
        for e in request:
            read = self.file.read(e)
            result.write(read)
            request.success(len(read))
        return result.getvalue()
    
    def close(self):
        self.file.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()

class LimitWriter:
    def __init__(self, file, limiter):
        self.file = file
        self.limiter = limiter
    
    def write(self, data):
        import io
        dataLength = len(data)
        data = io.BytesIO(data)
        request = self.limiter.request(dataLength)
        for e in request:
            self.file.write(data.read(e))
            request.success(e)
            
    def close(self):
        logger.debug('Close %s' % self.file)
        self.file.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
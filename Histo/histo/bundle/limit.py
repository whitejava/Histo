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
        self.interval = 0.01
        self.lastTime = None
        self.currentSpeed = 0
        from threading import Lock
        self.lock = Lock()
    
    def request(self, requestBytes):
        return Request(self, requestBytes)
    
    def requestBytes(self, limit):
        with self.lock:
            if self.needSleep():
                self.sleep()
            maxBytes = self.getMaxBytes()
            result = min(maxBytes, limit)
            self.emitSpeed(result)
            return result
    
    def success(self, size):
        pass
    
    def emitSpeed(self, size):
        currentTime = self.getCurrentTime()
        if self.lastTime is not None:
            timeDelta = currentTime - self.lastTime
            import math
            self.currentSpeed *= math.exp(-timeDelta)
        self.currentSpeed += size
        self.lastTime = currentTime
    
    def needSleep(self):
        maxBytes = self.getMaxBytes()
        stepBytes = self.maxSpeed * self.interval
        return stepBytes * 2 < maxBytes
    
    def sleep(self):
        import time
        time.sleep(self.interval)
        
    def getMaxBytes(self):
        result = int((self.maxSpeed/0.5 - self.currentSpeed) * self.interval)
        return max(1, result)
    
    def getCurrentTime(self):
        import time
        return time.clock()

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
            if requestBytes == 0:
                logger.error('Request bytes is 0')
            yield requestBytes
            remainBytes -= requestBytes

class LimitReader:
    def __init__(self, file, limiter):
        self.file = file
        self.limiter = limiter
    
    def read(self, limit):
        import io
        result = io.BytesIO()
        logger.debug('[ Request limiter')
        request = self.limiter.request(limit)
        logger.debug(' ]')
        for e in request:
            read = self.file.read(e)
            if not read:
                break
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
        self.file.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
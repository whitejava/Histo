class Limit:
    def __init__(self, bundle, writeSpeed, readSpeed):
        self.bundle = bundle
        self.writeLimiter = Limiter(writeSpeed)
        self.readLimiter = Limiter(readSpeed)
    
    def open(self, name, mode):
        f = self.bundle.open(name)
        if mode == 'rb':
            return LimitReader(f, self.readLimiter)
        elif mode == 'wb':
            return LimitWriter(f, self.writeLimiter)
        else:
            raise Exception('No such mode.')

class Limiter:
    def __init__(self, maxSpeed, interval = 1.0):
        self.maxSpeed = maxSpeed
        self.interval = interval
        self.currentSpeed = 0
        self.lastTime = 0
    
    def request(self, requestBytes):
        return Request(self, requestBytes)
    
    def requestBytes(self):
        pass
    
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
            requestBytes = self.limiter.requestBytes()
            if requestBytes > remainBytes:
                requestBytes = remainBytes
            yield requestBytes
            remainBytes -= requestBytes

class LimitReader:
    def __init__(self, file, limiter):
        self.file = file
        self.limiter = limiter
    
    def read(self, limit):
        import io
        result = io.BytesIO()
        request = self.limiter.requestBytes(limit)
        for e in request:
            read = self.file.read(e)
            result.write(read)
            request.success(len(read))
        return result.getvalue()

class LimitWriter:
    def __init__(self, file, limiter):
        self.file = file
        self.limiter = limiter
    
    def write(self, data):
        import io
        data = io.BytesIO(data)
        request = self.limiter.request(len(data))
        for e in request:
            self.file.write(data.read(e))
            request.success(e)
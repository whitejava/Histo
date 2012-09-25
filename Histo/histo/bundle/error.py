class Error:
    def __init__(self, bundle, probability):
        self.bundle = bundle
        self.simulator = ErrorSimulator(probability)
    
    def open(self, name, mode):
        self.simulateError()
        file = self.bundle.open(name, mode)
        if mode == 'wb':
            return ErrorWriter(file, self.simulator)
        elif mode == 'rb':
            return ErrorReader(file, self.simulator)
        else:
            raise Exception('No such mode.')
    
    def list(self):
        self.simulateError()
        return self.bundle.list()
    
    def delete(self, name):
        self.simulateError()
        return self.bundle.delete()
    
    def simulateError(self):
        return self.simulator.simulateError()

class ErrorSimulator:
    def __init__(self, probability):
        self.probability = probability
    
    def simulateError(self):
        if self.simulateHappen():
            self.simulateError2()
        
    def simulateHappen(self):
        import random
        return random.random() <= self.probability
    
    def simulateError2(self):
        raise Exception('Simulated error.')

class ErrorWriter:
    def __init__(self, file, simulator):
        self.file = file
        self.simulator = simulator
        self.pointError = PointError(simulator)
    
    def write(self, data):
        self.pointError.increasePointer(len(data))
        return self.file.write(data)
    
    def close(self):
        self.file.close()
        self.simulator.simulateError()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
    
class ErrorReader:
    def __init__(self, file, simulator):
        self.file = file
        self.simulator = simulator
        self.pointError = PointError(simulator)
    
    def read(self, limit):
        result = self.file.read(limit)
        self.pointError.increasePointer(len(result))
        return result
    
    def close(self):
        self.file.close()
        self.simulator.simulateError()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
        
class PointError:
    def __init__(self, simulator):
        self.pointer = 0
        self.simulator = simulator
        self.errorPoint = self.getRandomErrorPoint(simulator)
    
    def increasePointer(self, size):
        if self.errorPoint is not None:
            self.increasePointer2(size)
    
    def getRandomErrorPoint(self, simulator):
        if simulator.simulateHappen:
            self.errorPoint = self.getRandomErrorPoint2()
        else:
            self.errorPoint = None
    
    def getRandomErrorPoint2(self):
        import random
        return abs(random.gauss(0, 1024*1024))
    
    def increasePointer2(self, size):
        if self.pointer + size >= self.errorPoint:
            self.simulator.simulateError2()
        else:
            self.pointer += size
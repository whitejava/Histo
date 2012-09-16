class Delay:
    def __init__(self, bundle, delay):
        self.bundle = bundle
        self.delay = delay
    
    def open(self, name, mode):
        self.simulateDelay()
        return self.bundle.open(name, mode)
    
    def list(self):
        self.simulateDelay()
        return self.bundle.list()
    
    def delete(self, name):
        self.simulateDelay()
        return self.bundle.delete()
    
    def simulateDelay(self):
        delay = self.getGaussDelay()
        return self.delay2(delay)
    
    def getGaussDelay(self):
        import random
        return random.gauss(self.delay, 0.1)
    
    def delay2(self, delay):
        if delay < 0:
            delay = 0
        return self.delay3(delay)
    
    def delay3(self, delay):
        import time
        time.sleep(delay)
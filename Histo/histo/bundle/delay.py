import logging as logger

class Delay:
    def __init__(self, bundle, delay):
        self.bundle = bundle
        self.delay = delay
    
    def __getattr__(self, name):
        def result(*k, **kw):
            self.nap()
            return getattr(self.bundle, name)(*k, **kw)
        return result

    def nap(self):
        delay = self.getGaussDelay()
        return self.sleep(delay)
    
    def getGaussDelay(self):
        import random
        return abs(random.gauss(self.delay, 0.1))
    
    def sleep(self, duration):
        logger.debug('Sleep %s' % duration)
        import time
        time.sleep(duration)
import time

class timer:
    def __enter__(self):
        self._time = time.clock()
    
    def __exit__(self,*k):
        print(time.clock() - self._time)
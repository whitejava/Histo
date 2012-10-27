class PeriodEvent:
    def __init__(self, callable2, interval, exitEvent):
        self.callable = callable2
        self.interval = interval
        self.exitEvent = exitEvent
        from threading import Thread, Event
        self.request = Event()
        Thread(target = self.loopThread).start()
        Thread(target = self.listenExit).start()
    
    def loopThread(self):
        while True:
            self.request.wait(self.interval)
            if self.exitEvent.is_set():
                break
            self.request.clear()
            self.callable()
            
    def listenExit(self):
        self.exitEvent.wait()
        self.set()
    
    def set(self):
        self.request.set()

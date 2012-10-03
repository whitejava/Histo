import logging as logger

def main():
    Main().run()

class Main():
    def run(self):
        self.loadConfig()
        self.initLogger()
        self.initExitEvent()
        try:
            self.initStateBundle()
            self.initDataBundle()
            self.initServer()
            self.startServer()
            self.waitKeyboardInterruption()
        finally:
            self.shutdown()
    
    def loadConfig(self):
        import sys
        configFile = sys.argv[1]
        self.config = loadConfig(configFile)
    
    def initLogger(self):
        from histo.server.logger import initLogger
        config = self.config['Logger']
        initLogger(config)
    
    def initExitEvent(self):
        logger.debug('[ Init exit event')
        from threading import Event
        self.exitEvent = Event()
        logger.debug(' ]')
    
    def initStateBundle(self):
        logger.debug('[ Init state bundle')
        from histo.server.bundle import StateBundle
        config = self.config['StateBundle']
        self.stateBundle = StateBundle(config, self.exitEvent)
        logger.debug(' ]')
    
    def initDataBundle(self):
        logger.debug('[ Init data bundle')
        from histo.server.bundle import DataBundle
        config = self.config['DataBundle']
        self.dataBundle = DataBundle(config, self.exitEvent)
        logger.debug(' ]')
    
    def initServer(self):
        logger.debug('[ Init server')
        from histo.server.histoserver import HistoServer
        config = self.config['Server']
        stateBundle = self.stateBundle
        dataBundle = self.dataBundle
        event = self.exitEvent
        self.server = HistoServer(config, stateBundle, dataBundle)
        logger.debug(' ]')
    
    def startServer(self):
        logger.debug('[ Start server')
        self.server.start()
        logger.debug(' ]')
    
    def waitKeyboardInterruption(self):
        logger.debug('[ Wait keyboard interruption')
        waitForKeyboardInterruption()
        logger.debug(' ]')
    
    def shutdown(self):
        logger.debug('[ Shutdown')
        self.exitEvent.set()
        self.server.shutdown()
        logger.debug(' ]')

def loadConfig(file):
    with open(file, 'r') as f:
        import json
        return json.load(f)

def waitForKeyboardInterruption():
    try:
        sleepForever()
    except KeyboardInterrupt:
        logger.debug('On keyboard interrupt')

def sleepForever():
    while True:
        import time
        time.sleep(1)

if __name__ == '__main__':
    main()
from picklestream import PickleServer
class HistoServer(PickleServer):
    def __init__(self, config, stateBundle, dataBundle):
        self.config = config
        self.stateBundle = stateBundle
        self.dataBundle = dataBundle
        self.state = self.loadState()
        self.index = self.loadIndex()
        listenAddress = getListenAddress(config)
        PickleServer.__init__(self, listenAddress)
    
    def handle(self, stream):
        config = self.config
        state = self.state
        index = self.index
        dataBundle = self.dataBundle
        from histo.server.picklehandler import PickleHandler
        handler = PickleHandler(config, state, index, dataBundle, stream)
        handler.run()
    
    def loadState(self):
        from histo.server.state import State
        return State(self.stateBundle)
    
    def loadIndex(self):
        from histo.server.index import Index
        with self.openIndexCodesAsSingleStream() as f:
            return Index(f)
    
    def openIndexCodesAsSingleStream(self):
        bundle = self.dataBundle
        indexCodes = self.state['IndexCodes']
        return openCodesAsSingleStream(bundle, indexCodes)

def getListenAddress(config):
    listenIp = config['ListenIP']
    listenPort = config['ListenPort']
    return (listenIp, listenPort)

def openCodesAsStreams(bundle, codes):
    for e in codes:
        with bundle.open('data-%08d' % e, 'rb') as f:
            yield f
            
def openCodesAsSingleStream(bundle, codes):
    from histo.server.joinstream import JoinStream
    streams = openCodesAsStreams(bundle, codes)
    return JoinStream(streams)
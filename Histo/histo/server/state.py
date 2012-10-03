class State:
    def __init__(self, bundle):
        self.bundle = bundle
        self.state = self.loadOrCreateState()

    def update(self, state):
        self.state = state
        self.writeStateToBundle()

    def __getitem__(self, k):
        return self.state[k]
    
    def __setitem__(self, k, v):
        self.state[k] = v

    def writeStateToBundle(self):
        stateName = 'state-%04d%02d%02d%02d%02d%02d%06d' % self.state['Time']
        from histo.server.keysets import KeySets
        encodedState = KeySets.encode(0, self.state)
        import pickle
        pickledState = pickle.dumps(encodedState)
        stream = self.bundle.open(stateName, 'wb')
        from picklestream import PickleStream
        stream = PickleStream(stream)
        with stream as f:
            f.writeObject(pickledState)

    def loadOrCreateState(self):
        latestState = self.getLatestState()
        if latestState is None:
            return self.createState()
        else:
            return self.loadState(latestState)
        
    def getLatestState(self):
        states = self.bundle.list()
        if len(states) == 0:
            return None
        else:
            return list(sorted(states))[-1]
    
    def loadState(self, state):
        stream = self.bundle.open(state, 'rb')
        from picklestream import PickleStream
        stream = PickleStream(stream)
        with stream as f:
            return f.readObject()
    
    def createState(self):
        from pclib import nowtuple
        result = dict()
        result['Time'] = nowtuple()
        result['CommitCount'] = 0
        result['CodeCount'] = 0
        result['IndexCodes'] = []
        return result
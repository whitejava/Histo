class Get:
    def __init__(self, stream, index, dataBundle):
        self.stream = stream
        self.index = index
        self.dataBundle = dataBundle
        
    def run(self):
        self.parameters = self.readParameters()
        self.commit = self.lookUpCommitByCommitId()
        self.writeSize()
        self.writeData()
    
    def readParameters(self):
        return self.stream.readObject()
    
    def lookUpCommitByCommitId(self):
        commitId = self.parameters['CommitID']
        return self.index.getItemByCommitId(commitId)
    
    def writeSize(self):
        size = self.commit['Size']
        self.stream.writeObject(size)
    
    def writeData(self):
        bundle = self.dataBundle
        codes = self.commit['Codes']
        stream = self.stream
        size = self.commit['Size']
        with openCodesAsSingleStream(bundle, codes) as f:
            from pclib import copystream
            assert copystream(f, stream, size) == size

def openCodesAsStreams(bundle, codes):
    for e in codes:
        with bundle.open('data-%08d' % e, 'rb') as f:
            yield f
            
def openCodesAsSingleStream(bundle, codes):
    from histo.server.joinstream import JoinStream
    streams = openCodesAsStreams(bundle, codes)
    return JoinStream(streams)
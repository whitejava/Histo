from debuginfo import *

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
        with DebugInfo('Send data. Expect size: %d' % self.commit['Size']):
            with openDataCodes(self.dataBundle, self.commit) as f:
                with DebugInfo('Copy stream') as d:
                    from pclib import copystream
                    sendSize = copystream(f, self.stream, self.commit['Size'])
                    d.result = 'Send size: %d' % sendSize
                    assert sendSize == self.commit['Size']
        
def openDataCodes(bundle, commit):
    from histo.server.codes import openCodesAsSingleStream
    return openCodesAsSingleStream(bundle, commit['Codes'], 'data-{:08d}'.format)

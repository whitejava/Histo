import logging as logger

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
        logger.debug('[ Send data')
        bundle = self.dataBundle
        codes = self.commit['Codes']
        stream = self.stream
        size = self.commit['Size']
        logger.debug('Expect size: %d' % size)
        from histo.server.codes import openCodesAsSingleStream
        with openCodesAsSingleStream(bundle, codes, 'data-{:08d}'.format) as f:
            from pclib import copystream
            logger.debug('[ Copy stream')
            sendSize = copystream(f, stream, size)
            logger.debug(' ]')
            logger.debug('Send size: %d' % sendSize)
            assert sendSize == size
        logger.debug(' ]')
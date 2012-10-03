class Search:
    def __init__(self, stream, index):
        self.stream = stream
        self.index = index
    
    def run(self):
        self.readParameters()
        self.searchIndex()
        self.writeResult()
    
    def readParameters(self):
        stream = self.stream
        parameters = stream.readObject()
        self.parameters = parameters
    
    def searchIndex(self):
        parameters = self.parameters
        keywords = parameters['Keywords']
        index = self.index
        result = index.search(keywords)
        self.result = result
    
    def writeResult(self):
        result = self.result
        stream = self.stream
        stream.writeObject(result)

import logging as logger

class RequestHandler:
    def __init__(self, method, config, state, index, dataBundle, stream):
        self.method = method
        self.config = config
        self.state = state
        self.index = index
        self.dataBundle = dataBundle
        self.stream = stream
        
    def run(self):
        try:
            myCallable = self.lookUpCallableByMethod()
            myCallable()
        except Exception as e:
            logger.exception(e)
            raise
        
    def lookUpCallableByMethod(self):
        t = self.getMethodCallableDict()
        method = self.method
        result = t[method]
        return result

    def getMethodCallableDict(self):
        t = {'Commit': self.commit,
             'Search': self.search,
             'Get': self.get}
        return t

    def commit(self):
        config = self.config
        state = self.state
        index = self.index
        dataBundle = self.dataBundle
        stream = self.stream
        from histo.server.commit import Commit
        commit = Commit(config, state, index, dataBundle, stream)
        commit.run()
    
    def search(self):
        stream = self.stream
        index = self.index
        from histo.server.search import Search
        search = Search(stream, index)
        return search.run()
    
    def get(self):
        stream = self.stream
        index = self.index
        dataBundle = self.dataBundle
        from histo.server.get import Get
        get = Get(stream, index, dataBundle)
        result = get.run()
        return result
    
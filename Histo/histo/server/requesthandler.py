import logging as logger
from debuginfo import *

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
             'Get': self.get,
             'VerifyLocal': self.verifyLocal}
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
    
    def verifyLocal(self):
        verifyLocal(self.index, self.dataBundle, self.stream)

def verifyLocal(index, bundle, stream):
    with DebugInfo('Verify local'):
        for e in index:
            stream.writeObject('Verifying %04d-%s' % (e['CommitID'], e['Name']))
            r = verifySingleCommit(e, bundle)
            if r is not None:
                stream.writeObject(r)
        stream.writeObject('END')

def verifySingleCommit(commit, bundle):
    with DebugInfo('Verify commit: %04d-%s' % (commit['CommitID'],commit['Name'])) as d:
        actualHash = recalculateCommitMD5(commit, bundle)
        expectHash = commit['MD5']
        if actualHash != expectHash:
            from pclib import byteshex
            message = 'Verify failed: actual %s expect %s' % (byteshex.encode(actualHash), byteshex.encode(expectHash))
            d.result = message
            return message
        else:
            d.result = 'Success'
        
def recalculateCommitMD5(commit, bundle):
    with DebugInfo('Recalculating commit md5') as d:
        from histo.server.get import openDataCodes
        from pclib import hashstream
        hasher = hashstream('md5')
        with openDataCodes(bundle, commit) as f:
            from pclib import copystream
            copystream(f, hasher)
        result = hasher.digest()
        from pclib import byteshex
        d.result = byteshex.encode(result)
        return result
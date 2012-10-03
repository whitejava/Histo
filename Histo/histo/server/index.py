class Index:
    def __init__(self, stream):
        self.index = loadIndex(stream)
    
    def search(self, keyWords):
        matchCount = [countKeyWordsMatch(e['Summary'], keyWords) for e in self]
        result = [(e['Time'], e['CommitID'], e['Name'], e['Size'], e['MD5']) for e in self]
        return [dict(zip('Time CommitID Name Size MD5'.split(), e[1])) for e in sorted(zip(matchCount, result), reverse=True)]
    
    def add(self, encodedIndexItem):
        self.index.append(encodedIndexItem)
    
    def getItemByCommitId(self, commitId):
        for e in self:
            if e['CommitID'] == commitId:
                return e
        raise Exception('No such commit id')
    
    def __iter__(self):
        from histo.server.keysets import KeySets
        for e in self.index:
            yield KeySets.decode(e)

def loadIndex(stream):
    from picklestream import PickleStream
    stream = PickleStream(stream)
    result = []
    while True:
        try:
            result.append(stream.readObject())
        except EOFError:
            break
    return result

def countKeyWordsMatch(summary, keywords):
    result = 0
    for e in keywords:
        if isSummaryContainKeyword(summary, e):
            result += 1
    return result

def isSummaryContainKeyword(summary, keyword):
    from histo.server.summary import walk
    for e in walk(summary):
        if keyword in e:
            return True
    return False

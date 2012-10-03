class KeySets:
    @staticmethod
    def encode(keySetId, d):
        d = dict(d)
        result = []
        result.append(keySetId)
        for e in keySets[keySetId]:
            result.append(d[e])
            del d[e]
        assert not d
        return result
    
    @staticmethod
    def decode(x):
        return dict(zip(keySets[x[0]], x[1:]))

keySets = [
    ['Time', 'CommitCount', 'CodeCount', 'IndexCodes'],
    ['CommitID', 'Name', 'Time', 'Codes', 'Size', 'MD5', 'Summary'],
]

def main():
    keywords = input2('Keywords')
    result = search(keywords)
    printResult(result)
    selections = map(int, input2('Selections').split())
    for e in selections:
        download(result[e])
    
def input2(message):
    print(message + ': ', end='')
    return input()

def search(keywords):
    with connect() as conn:
        conn.writeObject('Search')
        p = {'Keywords': keywords}
        conn.writeObject(p)
        return conn.readObject()

def printResult(result):
    for i,e in reversed(list(enumerate(result))):
        time = '%04d%02d%02d' % e['Time'][:3]
        name = e['Name']
        print('%3d %s %s' % (i, time, name))

def download(commit, extractRoot = 'D:\\'):
    with connect() as conn:
        conn.writeObject('Get')
        p = {'CommitID' : commit['CommitID']}
        conn.writeObject(p)
        size = conn.readObject()
        fileName = '%04d-%s.rar' % (commit['CommitID'], commit['Name'])
        import os
        fileName = os.path.join(extractRoot, fileName)
        if os.path.exists(fileName):
            return False
        with open(fileName, 'wb') as f:
            from pclib import copystream
            assert size == copystream(conn, f, size)
        assert getFileMd5(fileName) == commit['MD5']
    return True

def connect():
    from picklestream import PickleClient
    return PickleClient(('127.0.0.1', 3750))

def getFileMd5(fileName):
    from pclib import copystream, hashstream
    result = hashstream('md5')
    with open(fileName, 'rb') as f:
        copystream(f, result)
    return result.digest()

if __name__ == '__main__':
    main()
def main():
    keywords = input2('Keywords')
    result = search(keywords)
    printResult(result)
    selections = map(int, input2('Selections').split())
    map(download, (result[e] for e in selections))
    
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
    for i,e in reversed(enumerate(result)):
        time = '%04d%02d%02d' % e['Time'][:3]
        name = e['Name']
        print('%3d %s %s' % (i, time, name))

def download(commit):
    with connect() as conn:
        conn.writeObject('Get')
        p = {'CommitID' : commit['CommitID']}
        conn.writeObject(p)
        size = conn.readObject()
        fileName = '%04d-%s' % (commit['CommitID'], commit['Name'])
        root = 'D:\\'
        import os
        fileName = os.path.join(root, fileName)
        with open(fileName, 'wb') as f:
            from pclib import copystream
            assert size == copystream(conn, f)

def connect():
    from picklestream import PickleClient
    return PickleClient('127.0.0.1', 3750)

if __name__ == '__main__':
    main()
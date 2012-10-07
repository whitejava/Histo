def main():
    root = 'G:\\recommit'
    import os
    files = os.listdir(root)
    files = [os.path.join(root, e) for e in files]
    files = [(os.path.getsize(e), e) for e in files]
    files = sorted(files)
    start = 0
    files = files[start:start+850]
    i = start
    for size,e in files:
        print('Commit: ', i, size, e)
        commit(e)
        i += 1

def commit(file):
    import os
    name = os.path.basename(file)
    assert name[20] == '-'
    
    time = (name[0:4],name[4:6],name[6:8],name[8:10],name[10:12],name[12:14],name[14:20])
    time = tuple(map(int, time))
    name = name[21:-4]
    
    from tempfile import TemporaryDirectory
    with TemporaryDirectory('.histo') as temp:
        temp = os.path.join(temp, 'a')
        os.mkdir(temp)
        from histo.server.summary import unpackArchive
        assert unpackArchive(file, temp) is None
        from histo.commit import advancedCommit
        advancedCommit(temp, time, name, True)

if __name__ == '__main__':
    main()
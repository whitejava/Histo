root = 'D:\\dfile'
key1 = b'0123456789abcdef'
key2 = b'0123456789abcdef0123'
key3 = b'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
partSize = 10

def getFiles():
    import dfile
    from files import LocalFiles
    from files import CipherFiles
    import crypto
    ciphers = []
    #ciphers.append(crypto.VerifyCipher('md5'))
    #ciphers.append(crypto.VerifyCipher('sha512'))
    #ciphers.append(crypto.XorCipher(key1, 'md5'))
    #ciphers.append(crypto.XorCipher(key2, 'sha1'))
    #ciphers.append(crypto.XorCipher(key3, 'sha512'))
    #ciphers.append(crypto.VerifyCipher('md5'))
    #ciphers.append(crypto.VerifyCipher('sha512'))
    files = LocalFiles(root)
    for e in ciphers:
        files = CipherFiles(files, e)
    return files

def testWrite():
    import dfile
    state = dfile.State(root, partSize)
    state.loadOrCreate()
    files = getFiles()
    f = dfile.Writer(state, files.openForWrite)
    try:
        for i in range(20):
            f.write(b'0124564'*1000)
    finally:
        f.close()
    print(f.getModify())

def testRead():
    import dfile
    state = dfile.State(root, partSize)
    state.load()
    files = getFiles()
    f = dfile.Reader(state, files.openForRead)
    try:
        r=f.read()
        print(len(r),r)
    finally:
        f.close()

def md5bytes(start, length):
    import hashlib
    r = b''
    for i in range(start,start+length):
        r += bytes([hashlib.md5(bytes(str(i),'utf8')).digest()[0]])
    return r

def testBulkWrite():
    import dfile
    import random
    state = dfile.State(root, partSize)
    state.loadOrCreate()
    files = getFiles()
    f = dfile.Writer(state, files.openForWrite)
    for i in range(10):
        f.write(md5bytes(f.tell(), random.randint(0,40)))
    f.close()

def testBulkRead():
    import dfile
    import random
    state = dfile.State(root, partSize)
    state.load()
    files = getFiles()
    f = dfile.Reader(state, files.openForRead)
    for i in range(100):
        size = f.getFileSize()
        start = random.randint(0,size)
        end = start + random.randint(0, 40)
        if end > size:
            end = size
        f.seek(start)
        length = end - start
        read = f.read(length)
        if md5bytes(start, end - start) != read:
            raise Exception('read error [{},{}] '.format(start,end) + ''.join(['{:02x}'.format(e)for e in read]))
    f.close()

#testBulkWrite()
testBulkRead()
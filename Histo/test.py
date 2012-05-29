root = 'D:\\dfile'
key1 = b'0123456789abcdef'
key2 = b'0123456789abcdef0123'
key3 = b'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
partSize = 1000000

def getFiles():
    import dfile
    from files import LocalFiles
    from files import CipherFiles
    import crypto
    ciphers = []
    ciphers.append(crypto.VerifyCipher('md5'))
    ciphers.append(crypto.VerifyCipher('sha512'))
    ciphers.append(crypto.XorCipher(key1, 'md5'))
    ciphers.append(crypto.XorCipher(key2, 'sha1'))
    ciphers.append(crypto.XorCipher(key3, 'sha512'))
    ciphers.append(crypto.VerifyCipher('md5'))
    ciphers.append(crypto.VerifyCipher('sha512'))
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

testWrite()
testRead()
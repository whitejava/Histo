root = 'D:\\dfile'
key1 = b'0123456789abcdef'
key2 = b'0123456789abcdef0123'
key3 = b'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
partSize = 10

import random

def oneRun():
    deleteDFile()
    testCorrectness()
    testPartMissing()
    testPartCorrupt()
    testDecryptError()
    testFileTruncate()

for i in range(100):
    print('Case {}: Running... ', end = '')
    oneRun()
    print('OK')

def getFiles():
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

def md5bytes(it):
    import hashlib
    r = b''
    for i in it:
        r += bytes([hashlib.md5(bytes(str(i),'utf8')).digest()[0]])
    return r

def createWriter():
    import dfile
    state = dfile.State(root, partSize)
    state.loadOrCreate()
    files = getFiles()
    f = dfile.Writer(state, files.openForWrite)
    return f

def createReader():
    import dfile
    state = dfile.State(root, partSize)
    state.load()
    files = getFiles()
    f = dfile.Reader(state, files.openForRead)
    return f

def writeRandom(f):
    start = f.tell()
    length = random.randint(0, 40)
    f.write(md5bytes(range(start, start + length)))

def testBulkWrite():
    f = createWriter()
    for i in range(10):
        writeRandom(f)
    f.close()

def readRandom(f):
    size = f.getFileSize()
    start = random.randint(0,size)
    end = start + random.randint(0, 40)
    if end > size:
        end = size
    f.seek(start)
    length = end - start
    return {'start':start,'end':end,'data':f.read(length)}

def testBulkRead():
    f = createReader()
    try:
        for i in range(1000):
            r = readRandom(f)
            if md5bytes(range(r['start'],r['end'])) != r['data']:
                raise Exception('read error [{},{}] '.format(r['start'],r['end']) + ''.join(['{:02x}'.format(e)for e in r['data']]))
    finally:
        f.close()

def deleteDFile():
    import shutil
    shutil.rmtree(root)

def testNormal():
    testBulkWrite()
    testBulkRead()
    deleteDFile()

def getParts():
    import os
    a = os.walk(root)[2]
    a.remove('state')
    for e in a:
        os.path.join(root,e)

def deleteAllParts():
    for e in getParts():
        os.remove(e)

def readExpectMissingPart(f):
    import dfile
    error = None
    try:
        r = readRandom(f)
    except dfile.MissingPart as e:
        error = e
    finally:
        f.close()
    if not error:
        raise Exception('expect missing part, but read ' + r)

def testReadMissingPart():
    f = createReader()
    for i in range(1000):
        readExpectMissingPart()
    f.close()

def testPartMissing():
    testBulkWrite()
    deleteAllParts()
    testReadMissingPart()

def getFileSize(filename):
    import os
    return os.path.getsize(filename)

def corrupt(filename):
    size = getFileSize(filename)
    with open(filename,'r+b') as f:
        pos = random.randint(0,size-1)
        f.seek(pos)
        raw = f.read(1)
        f.seek(pos)
        f.write(random.sample(range(256).remove(raw)))

def corruptEveryPartOneBit():
    for e in getParts():
        corrupt(e)

def readDataCorrupt(f):
    import dfile
    error = None
    try:
        r = readRandom(f)
    except dfile.DataCorrupt as e:
        error = e
    if not error:
        raise Exception('expect DataCorrupt but read ' + r)

def testReadDataCorrupt():
    f = createReader()
    for i in range(1000):
        readDataCorrupt(f)
    f.close()

def testDataCorrupt():
    testBulkWrite()
    corruptEveryPartOneBit()
    testReadDataCorrupt()

def testKeyError():
    testBulkWrite()
    

import os
if os.path.exists(root):
    deleteDFile()
for i in range(100):
    print('Case {}: Testing...'.format(i+1), end = '')
    testNormal()
    print('OK')
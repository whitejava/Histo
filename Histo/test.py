root = 'D:\\dfile'
key1 = b'0123456789abcdef'
key2 = b'0123456789abcdef0123as'
key3 = b'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
key4 = b'fdas123f1dsa35fd'
key5 = b'fd5as6f4ds5a6f4dsa5fsa'
key6 = b'fdsa4f45d6sa18c9e18aw49r98a1fd8as9fd4safdsa9618cd9as1f8dsa94fd8d'
keySet1 = [key1, key2, key3]
keySet2 = [key4, key5, key6]
partSize = 10

import random
import dfile

def createCiphers(keys = keySet1):
    from crypto import VerifyCipher
    from crypto import XorCipher
    r = []
    r.append(VerifyCipher('md5'))
    r.append(VerifyCipher('sha1'))
    r.append(XorCipher(keys[0], 'md5'))
    r.append(XorCipher(keys[1], 'sha1'))
    r.append(XorCipher(keys[2], 'sha512'))
    r.append(VerifyCipher('md5'))
    r.append(VerifyCipher('sha1'))
    return r

def createFiles(keys = keySet1):
    from files import LocalFiles
    from files import CipherFiles
    files = LocalFiles(root)
    ciphers = createCiphers(keys)
    for e in ciphers:
        files = CipherFiles(files, e)
    return files

def createState():
    return dfile.State(root, partSize)

def createReader(keys = keySet1):
    s = createState()
    s.load()
    return dfile.Reader(s, createFiles(keys))

def getPartCount():
    import os
    return len(list(os.walk(root))[0][2])-1

def randomBoolean():
    return random.randint(0,1) == 0

def randomParts():
    r = []
    for e in range(getPartCount()):
        if randomBoolean():
            r.append(e)
    return r

def randomRange(f):
    size = f.getFileSize()
    start = random.randint(0, size)
    end = start + random.randint(0, 40)
    end = min(size, end)
    return range(start, end)

def md5(a):
    import hashlib
    return hashlib.md5(a).digest()

def getData(ra):
    r = b''
    for e in ra:
        r += bytes([md5(bytes(str(e),'utf8'))[0]])
    return r

def readRange(f, ra):
    if ra:
        f.seek(ra[0])
        return f.read(len(ra))
    else:
        return b''

def readCorrect(f, ra = None):
    if not ra:
        ra = randomRange(f)
    expect = getData(ra)
    actual = readRange(f, ra)
    assert expect == actual

def randomLength():
    return random.randint(0, 40)

def writeData(f, length):
    p = f.tell()
    length = randomLength()
    ra = range(p, p + length)
    data = getData(ra)
    f.write(data)

def writeRandom(f):
    writeData(f, randomLength())

def createWriter():
    s = createState()
    s.loadOrCreate()
    return dfile.Writer(s, createFiles())

def bulkWrite():
    with createWriter() as f:
        for _ in range(random.randint(0,3)):
            writeRandom(f)

def writeOneBit():
    with createWriter() as f:
        writeData(f, 1)

def multiBulkWrite():
    writeOneBit()
    for _ in range(random.randint(1, 4)):
        bulkWrite()

def deleteDFile():
    import shutil
    try:
        shutil.rmtree(root)
    except:
        pass

def testBulkWrite():
    print('Testing BulkWrite')
    multiBulkWrite()
        
def testCorrectRead():
    print('Testing CorrectRead')
    with createReader() as f:
        for _ in range(1000):
            readCorrect(f)

def readRandom(f):
    ra = randomRange()
    return readRange(f, ra)
        
def readExpectError(f, err, ra = None):
    if not ra: ra = randomRange(f)
    try:
        r = readRange(f, ra)
    except err:
        return
    raise Exception('Expect error, but read ' + ''.join(['{:02x}'.format(e) for e in r]))

def testDecryptError():
    import crypto
    print('Testing DecryptError')
    with createReader(keySet2) as f:
        for _ in range(1000):
            ra = randomRange(f)
            if ra:
                readExpectError(f,crypto.VerifyError, ra)
            else:
                assert readRange(f, ra) == b'' 

def contains(a,b):
    for e in b:
        for f in a:
            if e == f:
                return True
    return False

def getPartId(a):
    return a // partSize

def relatedParts(ra):
    if ra:
        start = ra[0]
        end = start + len(ra) - 1
        return list(range(getPartId(start), getPartId(end)+1))
    else:
        return []

def readDataCorrupt(f, parts):
    import crypto
    ra = randomRange(f)
    print('read range', repr(ra))
    print('related',repr(relatedParts(ra)))
    if contains(parts, relatedParts(ra)):
        readExpectError(f, crypto.VerifyError, ra)
    else:
        readCorrect(f, ra)

def getPartFileName(n):
    import os
    return os.path.join(root, '{:04d}'.format(n))

def openPart(n,mode='r+b'):
    return open(getPartFileName(n),mode)

def getFileLength(file):
    import os
    return os.path.getsize(file.name)

def randomByteFrom(sample):
    return bytes([random.sample(sample,1)[0]])

def randomByteExcept(ex):
    r = list(range(256))
    for e in set(list(ex)):
        r.remove(e)
    return randomByteFrom(r)

def corruptFile(f):
    length = getFileLength(f)
    p = random.randint(0, length-1)
    f.seek(p)
    before = f.read(1)
    after = randomByteExcept(before)
    f.seek(p)
    f.write(after)

def corruptPart(n):
    with openPart(n) as f:
        corruptFile(f)

def corruptParts(parts):
    for e in parts:
        corruptPart(e)

def testDataCorrupt():
    print('Testing DataCorrupt')
    parts = randomParts()
    corruptParts(parts)
    print('corrupt parts',repr(parts))
    with createReader() as f:
        for _ in range(1000):
            readDataCorrupt(f, parts)

def deleteFileName(fileName):
    import os
    os.remove(fileName)

def deletePart(part):
    deleteFileName(getPartFileName(part))

def deleteParts(parts):
    for e in parts:
        deletePart(e)

def readPartMissing(f, missing):
    ra = randomRange()
    if contains(missing, relatedParts(ra)):
        readExpectError(f, dfile.MissingPart, ra)
    else:
        readCorrect(f, ra)

def testPartMissing():
    print('Testing PartMissing')
    parts = randomParts()
    deleteParts(parts)
    with createReader() as f:
        for _ in range(1000):
            readPartMissing(f, parts)

def deployDFile():
    print('Deploy File')
    deleteDFile()
    multiBulkWrite()

def oneRun():
    deleteDFile()
    testBulkWrite()
    #testCorrectRead()
    #testDecryptError()
    testDataCorrupt()
    deployDFile()
    testPartMissing()
    deleteDFile()

def bigTest():
    for i in range(100):
        print('Case {}:'.format(i+1))
        oneRun()
        print('OK')

def temp():
    with createReader() as f:
        readRange(f, range(94,110))
        readRange(f, range(87,87))

bigTest()
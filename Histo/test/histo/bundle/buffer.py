def main():
    import logging
    global logger
    format = '%(asctime)s %(thread)08d %(message)s'
    logging.basicConfig(format=format, level=logging.DEBUG)
    from pclib import timetext
    handler = logging.FileHandler('D:\\%s.log' % timetext())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(format))
    logger = logging.getLogger()
    logger.addHandler(handler)
    bundle = Bundle()
    global files
    files = []
    from itertools import count
    global fileNames
    fileNames = map(getFileName, count(0))
    for _ in range(10):
        TestThread(bundle).start()

def getFileName(x):
    import hashlib
    import base64
    return str(base64.b16encode(hashlib.md5(bytes(str(x),'utf8')).digest()),'utf8')[:8].lower()

def Bundle():
    from histo.bundle import Buffer
    import os
    from pclib import timetext
    from histo.bundle import Local, Crypto
    root = 'D:\\%s-test-buffer' % timetext()
    fast = Local(os.path.join(root, 'fast'))
    slow = Slow(os.path.join(root, 'slow'))
    return slow
    queueFile = os.path.join(root, 'queue')
    usageLogFile = os.path.join(root, 'usage-log')
    maxBufferSize = 10*1024*1024
    threadCount = 10
    result = Buffer(fast, slow, queueFile, usageLogFile, maxBufferSize, threadCount)
    result = Crypto(result, Cipher())
    return result

def Fast(root):
    from histo.bundle import Local
    return Local(root)

def Slow(root):
    #return Fast(root)
    from histo.bundle import Error, Delay, Limit, Local
    result = Local(root)
    result = Error(result, 0.1)
    result = Limit(result, 200000, 200000)
    result = Delay(result, 1.0)
    return result

def Cipher():
    key = b'1'*32
    from histo.cipher import AES, Verify, Hub
    return Hub(Verify('md5'), AES(key), Verify('md5'))

def TestThread(bundle):
    from threading import Thread
    return Thread(target=testLoop, args=(bundle,))
    
def testLoop(bundle):
    for _ in range(10000):
        try:
            randomAction(bundle)
        except Exception as e:
            logger.exception(e)

def randomAction(bundle):
    actions = [testWrite, testRead, testList]
    import random
    random.choice(actions)(bundle)

def testList(bundle):
    logger.debug('Test list')
    logger.debug('Length %d' % len(bundle.list()))

def testWrite(bundle):
    file = next(fileNames)
    logger.debug('Test write %s' % file)
    with bundle.open(file, 'wb') as f:
        f.write(FileData(file))
    files.append(file)
    logger.debug('Finish write %s' % file)

def testRead(bundle):
    logger.debug('Test read')
    import random
    if not files:
        return
    file = random.choice(files)
    logger.debug('File %s' % file)
    with bundle.open(file, 'rb') as f:
        logger.debug('Opened file')
        logger.debug('Reading')
        assert readAll(f) == FileData(file)
    logger.debug('Finish read %s' % file)

def readAll(file):
    import io
    result = io.BytesIO()
    import random
    while True:
        length = abs(int(random.gauss(100,100))) + 1
        logger.debug('Reading %s' % length)
        read = file.read(length)
        if not read:
            break
        logger.debug('Read Result %s' % len(read))
        result.write(read)
    return result.getvalue()

def FileData(file):
    from random import Random
    r = Random(file)
    length = abs(int(r.gauss(1024*1024,1024*1024)))
    return bytes([r.randrange(256) for _ in range(length)])

if __name__ == '__main__':
    main()
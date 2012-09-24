def main():
    import logging
    global logger
    logging.basicConfig(format='$asctime $module $thread $message', style='$', level=logging.DEBUG)
    logger = logging.getLogger()
    bundle = Bundle()
    global files
    files = []
    from itertools import count
    global fileNames
    fileNames = map(str, count(0))
    for _ in range(10):
        TestThread(bundle).start()

def Bundle():
    from histo.bundle import Buffer
    import os
    from pclib import timetext
    from histo.bundle import Local, Crypto
    root = 'D:\\%s-test-buffer' % timetext()
    fast = Local(os.path.join(root, 'fast'))
    slow = Slow(os.path.join(root, 'slow'))
    queueFile = os.path.join(root, 'queue')
    usageLogFile = os.path.join(root, 'usage-log')
    maxBufferSize = 100*1024*1024
    threadCount = 10
    return Crypto(Buffer(fast, slow, queueFile, usageLogFile, maxBufferSize, threadCount), Cipher())

def Fast(root):
    from histo.bundle import Local
    return Local(root)

def Slow(root):
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
    while True:
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
        assert readAll(f) == FileData(file)
    logger.debug('Finish read %s' % file)

def readAll(file):
    import io
    result = io.BytesIO()
    import random
    while True:
        length = abs(int(random.gauss(100,100))) + 1
        read = file.read(length)
        if not read:
            break
        result.write(read)
    return result.getvalue()

def FileData(file):
    from random import Random
    r = Random(file)
    length = abs(int(r.gauss(1024*1024,1024*1024)))
    return bytes([r.randrange(256) for _ in range(length)])

if __name__ == '__main__':
    main()
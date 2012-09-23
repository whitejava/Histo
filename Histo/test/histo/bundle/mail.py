def main():
    import logging
    global logger
    logging.basicConfig(format='$asctime $thread $message', level=logging.DEBUG, style='$')
    logger = logging.getLogger()
    bundle = Bundle()
    #testSingleThread(bundle)
    testThreading(bundle)

def testSingleThread(bundle):
    from pclib import timetext
    name = timetext()
    testList(bundle)
    testWrite(bundle, name)
    testRead(bundle, name)

def Bundle():
    from histo.bundle import Mail
    return Mail('imap.gmail.com', 993, 'cpc.histo.d0', 'fae39928ef', 'cpc.histo.d0@gmail.com', 'histo@caipeichao.com')

def testList(bundle):
    logger.debug('Test list')
    logger.debug(str(bundle.list()))

def testWrite(bundle, name):
    logger.debug('Test write ' + name)
    with bundle.open(name, 'wb') as f:
        for _ in range(100):
            f.write(b'a'*1024)
    logger.debug('Write ok ' + name)

def testRead(bundle, name):
    logger.debug('Test read ' + name)
    with bundle.open(name, 'rb') as f:
        read = readAll(f)
        assert read == b'a'*100*1024
    logger.debug('Read ok ' + name)

def readAll(file):
    import io
    result = io.BytesIO()
    while True:
        read = file.read(1024)
        if not read:
            break
        result.write(read)
    return result.getvalue()

def testThreading(bundle):
    for _ in range(10):
        TestThread(bundle).start()

def TestThread(bundle):
    from threading import Thread
    return Thread(target=actionLoop, args=(bundle,))

def actionLoop(bundle):
    for _ in range(1000):
        randomAction(bundle)

def randomAction(bundle):
    try:
        randomAction2(bundle)
    except Exception as e:
        logger.exception(e)

def randomAction2(bundle):
    actions = [testList, testRead2, testWrite2]
    import random
    return random.choice(actions)(bundle)

def testRead2(bundle):
    file = randomFile()
    logger.debug('Test read ' + file)
    with bundle.open(file, 'rb') as f:
        assert readAll(f) == FileData(file)
    logger.debug('Read ok ' + file)

def testWrite2(bundle):
    file = randomFile()
    logger.debug('Test write ' + file)
    with bundle.open(file, 'wb') as f:
        f.write(FileData(file))
    logger.debug('Write ok ' + file)

def FileData(file):
    from random import Random
    r = Random(file)
    length = r.randrange(100000)
    return bytes([r.randrange(256) for _ in range(length)])

def randomFile():
    import random
    return str(random.randrange(10))

if __name__ == '__main__':
    main()
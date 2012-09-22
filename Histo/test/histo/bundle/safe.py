def main():
    global salt
    salt = Salt()
    global logger
    import logging
    logging.basicConfig(format='$asctime $thread $message', level=logging.DEBUG, style='$')
    logger = logging.getLogger()
    bundle = Bundle()
    for _ in range(100):
        TestThread(bundle).start()

def Salt():
    return '123456'
    import random
    return bytes([random.randrange(256) for _ in range(32)])

def Bundle():
    from histo.bundle import Local, Safe
    from pclib import timetext
    return Safe(Local('D:\\%s-test-safe' % timetext()))

def TestThread(bundle):
    from threading import Thread
    return Thread(target = test, args = (bundle,))

def test(bundle):
    for _ in range(10000):
        randomAction(bundle)

def randomAction(bundle):
    try:
        randomAction2(bundle)
    except AssertionError as e:
        logger.debug('Assertion error %s' % e)
    except Exception as e:
        logger.exception(e)

def randomAction2(bundle):
    actions = [read, write, list2, delete]
    import random
    random.choice(actions)(bundle)

def read(bundle):
    file = randomFile()
    logger.debug('Start Read %s' % file)
    read = readAll(bundle.open(file, 'rb'))
    logger.debug('Read size %d' % len(read))
    assert read == FileData(file)
    logger.debug('End Read %s success' % file)

def write(bundle):
    file = randomFile()
    logger.debug('Write %s' % file)
    writeAll(bundle.open(file, 'wb'), FileData(file))
    logger.debug('Write %s success' % file)

def list2(bundle):
    logger.debug('List start')
    for e in bundle.list():
        print(e)
    logger.debug('List end')

def delete(bundle):
    file = randomFile()
    logger.debug('Delete %s' % file)
    bundle.delete(file)
    logger.debug('Delete %s success' % file)

def randomFile():
    import random
    return '%d' % random.randrange(10)

def FileData(file):
    import random
    r = random.Random(file + salt)
    length = r.randrange(100000)
    return bytes([r.randrange(256) for _ in range(length)]) 

def readAll(file):
    import io
    result = io.BytesIO()
    while True:
        read = file.read(1)
        if not read:
            break
        result.write(read)
    return result.getvalue()

def writeAll(file, data):
    for e in data:
        file.write(bytes([e]))

if __name__ == '__main__':
    main()
def main():
    initLogger()
    global limiter
    global counter
    counter = 0
    limiter = Limiter()
    for _ in range(5):
        TestThread().start()

def initLogger():
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

def Limiter():
    from histo.bundle.limit import Limiter
    return Limiter(100000)

def TestThread():
    from threading import Thread
    return Thread(target=threadProc)

def threadProc():
    while True:
        for e in limiter.request(randomSize()):
            global counter
            counter += e
            logger.debug('Got %10d Total %10d' % (e, counter))

def randomSize():
    import random
    return int(abs(random.gauss(100,100))) + 1

if __name__ == '__main__':
    main()
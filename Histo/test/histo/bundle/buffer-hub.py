def main():
    initLogger()
    from bundle import testBundle
    testBundle(Bundle())

def initLogger():
    import logging
    from pclib import timetext
    format2 = '%(asctime)s %(thread)08d %(message)s'
    logging.basicConfig(format=format2,level=logging.DEBUG)
    global logger
    logger = logging.getLogger()
    handler = logging.FileHandler('D:\\%s.log' % timetext())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(format2))
    logger.addHandler(handler)

def Bundle():
    from pclib import timetext
    import os.path
    root = 'D:\\%s' % timetext()
    L2 = BufferBundle(os.path.join(root, 'L2'))
    L1 = BufferBundle(os.path.join(root, 'L1'), L2)
    L0 = BufferBundle(os.path.join(root, 'L0'), L1)
    return L0
    
def BufferBundle(root, slowBundle=None):
    from histo.bundle import Buffer, Local
    import os.path
    fastBundle = Local(os.path.join(root, 'Fast'))
    if slowBundle is None:
        slowBundle = HubBundle(os.path.join(root, 'Slow'))
    queueFile = os.path.join(root, 'queue.txt')
    usageLogFile = os.path.join(root, 'usage-log.txt')
    maxBufferSize = 100
    threadCount = 3
    return Buffer(fastBundle, slowBundle, queueFile, usageLogFile, maxBufferSize, threadCount)

def HubBundle(root):
    count = 100
    from histo.bundle import Local, Hub
    import os.path
    bundles = [Local(os.path.join(root, 'part%02d' % i)) for i in range(count)]
    return Hub(bundles, [10000000]*count, {'Usage':[0]*count})

if __name__ == '__main__':
    main()
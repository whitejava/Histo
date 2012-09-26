def main():
    initLogger()
    from bundle import testBundle
    testBundle(Bundle())

def initLogger():
    import logging
    format2='%(asctime)s %(thread)s %(message)s'
    logging.basicConfig(format=format2, level=logging.DEBUG)
    global logger
    logger = logging.getLogger()
    from pclib import timetext
    handler = logging.FileHandler('D:\\%s.log' % timetext())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(format2))
    logger.addHandler(handler)

def Bundle():
    from histo.bundle import Local, Hub
    from pclib import timetext
    import os.path
    root = 'D:\\%s' % timetext()
    bundles = [Local(os.path.join(root, 'part%02d' % i)) for i in range(10)]
    return Hub(bundles, [10000000]*10, {'Usage':[0]*10})

if __name__ == '__main__':
    main()
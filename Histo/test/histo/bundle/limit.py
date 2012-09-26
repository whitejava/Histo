def main():
    initLogger()
    from bundle import testBundle
    testBundle(Bundle())

def initLogger():
    import logging
    global logger
    format = '[%(asctime)s] %(thread)08d %(message)s'
    logging.basicConfig(format=format, level=logging.DEBUG)
    from pclib import timetext
    handler = logging.FileHandler('D:\\%s.log' % timetext())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(format))
    logger = logging.getLogger()
    logger.addHandler(handler)

def Bundle():
    from histo.bundle import Local, Limit
    from pclib import timetext
    return Limit(Local('D:\\%s' % timetext()), 200000, 200000)
    
if __name__ == '__main__':
    main()
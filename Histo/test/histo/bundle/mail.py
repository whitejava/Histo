def main():
    initLogger()
    from bundle import testBundle
    testBundle(Bundle(), threadCount=1)

def initLogger():
    import logging
    logFormat = '%(asctime)s %(thread)08d %(message)s'
    logging.basicConfig(format=logFormat, level=logging.DEBUG)
    from pclib import timetext
    handler = logging.FileHandler('D:\\%s.txt' % timetext())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(logFormat))
    global logger
    logger = logging.getLogger()
    logger.addHandler(handler)

def Bundle():
    from histo.bundle import Mail
    host = 'imap.gmail.com'
    port = 993
    user = 'cpc.histo.d0'
    password = 'fae39928ef'
    sender = 'histo@caipeichao.com'
    receiver = 'cpc.histo.d0@gmail.com'
    from threading import Event
    return Mail(host, port, user, password, receiver, sender, Event())

if __name__ == '__main__':
    main()
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
    imap = dict()
    imap['Host'] = 'imap.gmail.com'
    imap['Port'] = 993
    imap['User'] = 'cpc.histo.d0'
    imap['Password'] = 'fae39928ef'
    smtp = dict()
    smtp['Host'] = 'smtp.gmail.com'
    smtp['Sender'] = 'histo@caipeichao.com'
    smtp['Receiver'] = 'cpc.histo.d0@gmail.com'
    config = dict()
    config['Imap'] = imap
    config['Smtp'] = smtp
    from threading import Event
    return Mail(config, Event())

if __name__ == '__main__':
    main()
def main():
    initLogger()
    global bundle
    bundle = Bundle()
    from bundle import testBundle
    testBundle(bundle)
    
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
    maxBufferSize = 10*1024*1024
    threadCount = 10
    result = Buffer(fast, slow, queueFile, usageLogFile, maxBufferSize, threadCount)
    result = Crypto(result, Cipher())
    return result

def Fast(root):
    from histo.bundle import Local
    return Local(root)

def Slow(root):
    #from histo.bundle import Mail
    #return Mail('imap.gmail.com', 993, 'cpc.histo.d0', 'fae39928ef', 'cpc.histo.d0@gmail.com', 'histo@caipeichao.com')
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

if __name__ == '__main__':
    main()
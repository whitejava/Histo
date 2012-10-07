def StateBundle(config, exitSignal):
    return FinalBundle(config, exitSignal)

def DataBundle(config, exitSignal):
    return FinalBundle(config, exitSignal)

def FinalBundle(config, exitSignal):
    from histo.bundle import Local, Buffer, Hub, Crypto
    fastBundle = Local(config['CachePath'])
    mailBundles = MailBundles(config['MailBundles'], exitSignal)
    slowBundle = Hub(mailBundles)
    cipher = Cipher(config['Cipher'])
    queueFile = config['QueueFile']
    usageLogFile = config['UsageLogFile']
    maxBufferSize = config['MaxBufferSize']
    threadCount = config['ThreadCount']
    buffer = Buffer(fastBundle, slowBundle, queueFile, usageLogFile, maxBufferSize, threadCount, exitSignal)
    return Crypto(buffer, cipher)

def MailBundles(config, exitSignal):
    return [Mail(e, exitSignal) for e in config]

def Cipher(config):
    from histo.cipher import Hub, AES, Verify
    from base64 import b16decode
    return Hub(Verify('md5'), AES(b16decode(bytes(config['Key'].upper(), 'utf8'))), Verify('sha1'), Verify('md5'))

def Mail(config, exitSignal):
    from histo.bundle import Mail as Mail2
    host = config['Host']
    port = config['Port']
    user = config['User']
    password = config['Password']
    receiver = config['Receiver']
    sender = config['Sender']
    volume = config['Volume']
    result = Mail2(host, port, user, password, receiver, sender, exitSignal)
    result.getVolume = lambda:volume
    return result

def SimMail(config, exitSignal):
    from histo.bundle import Error, Delay, Limit, Local
    volume = config['Volume']
    result = Local('D:\\sim-mail\\%s' % config['User'])
    result.getVolume = lambda:volume
    result = Error(result, 0.1)
    result = Limit(result, 200000, 200000)
    result = Delay(result, 1.0)
    return result

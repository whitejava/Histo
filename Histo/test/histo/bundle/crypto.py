def main():
    bundle = Bundle()
    size = testWrite(bundle)
    testRead(bundle, size)

def Bundle():
    from histo.bundle import Local, Crypto
    from pclib import timetext
    return Crypto(Local('D:\\%s-test-crypto' % timetext()), Cipher())

def testWrite(bundle):
    with bundle.open('test', 'wb') as f:
        return testWrite2(f)

def testRead(bundle, size):
    with bundle.open('test', 'rb') as f:
        testRead2(f, size)

def Cipher():
    from histo.cipher import Hub
    return Hub(Verify2(), Cipher2(), AES2(), Cipher2(), Verify2())

def Cipher2():
    from histo.cipher import Hub
    return Hub(Verify2(), AES2(), Verify2(), AES2(), Verify2())

def Verify2():
    from histo.cipher import Verify
    return Verify('md5')

def AES2():
    from histo.cipher import AES
    return AES(randomKey())

def testWrite2(file):
    size = 0
    for _ in range(10000):
        import random
        e = abs(int(random.gauss(16,16)))
        size += e
        file.write(b'a'*e)
    return size

def testRead2(file, size):
    readSize = 0
    while True:
        import random
        e = random.randrange(1,100)
        read = file.read(e)
        if not read:
            break
        readSize += len(read)
    assert readSize == size

def randomKey():
    import random
    return bytes([random.randrange(256) for _ in range(32)])

if __name__ == '__main__':
    test()
def test():
    from histo.bundle import Local
    from pclib import timetext
    from histo.cipher import AES, Hub, Verify
    key1 = b'1' * 32
    key2 = b'2' * 32
    cipher = Hub(Verify('md5'), AES(key2), Verify('md5'), AES(key1), Verify('md5'))
    bundle = Crypto(Local('D:\\%s-test-Crypto' % timetext()), cipher)
    size = 0
    with bundle.open('test', 'wb') as f:
        for _ in range(10000):
            import random
            e = abs(random.gauss(0, 100000))
            size += e
            f.write('a' * e)
    with bundle.open('test', 'rb') as f:
        while True:
            a = f.read(1000)
            if not a:
                break
            assert a == 'a' * len(a)
            size -= len(a)
    assert size == 0

if __name__ == '__main__':
    test()
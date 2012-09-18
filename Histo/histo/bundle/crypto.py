__all__ = ['Crypto']

class Crypto:
    def __init__(self, bundle, cipherFactory):
        self.bundle = bundle
        self.cipherFactory = cipherFactory
    
    def open(self, name, mode):
        file = self.bundle.open(name, mode)
        if mode == 'wb':
            return CryptoWriter(file, self.cipherFactory.encrypt())
        elif mode == 'rb':
            return CryptoReader(file, self.cipherFactory.decrypt())
        else:
            raise Exception('No such mode.')
    
    def delete(self, name):
        return self.bundle.delete(name)
    
    def list(self):
        return self.bundle.list()

class CryptoWriter:
    def __init__(self, file, cipher):
        self.file = file
        self.cipher = cipher
    
    def write(self, data):
        self.file.write(self.cipher.update(data))
    
    def close(self):
        self.file.write(self.cipher.final())
        self.file.close()

class CryptoReader:
    def __init__(self, file, cipher):
        self.file = file
        self.cipher = cipher
        self.buffer = b''
        self.generator = self.decryptionGenerator()
    
    def read(self, limit):
        result = self.read2(limit)
        self.buffer = result[limit:]
        return result[:limit]
    
    def close(self):
        self.file.close()

    def decryptionGenerator(self):
        trunkSize = 4*1024
        while True:
            read = self.file.read(trunkSize)
            if not read:
                break
            yield self.cipher.update(read)
        yield self.cipher.final()
    
    def read2(self, limit):
        import io
        result = io.BytesIO(self.buffer)
        try:
            while result.tell() < limit:
                result.write(next(self.generator))
        except StopIteration:
            pass
        return result.getvalue()

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
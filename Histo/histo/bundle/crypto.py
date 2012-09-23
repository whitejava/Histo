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
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()

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

    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()

    def decryptionGenerator(self):
        trunkSize = 4*1024
        while True:
            read = self.file.read(trunkSize)
            if not read:
                break
            result = self.cipher.update(read)
            yield result
        yield self.cipher.final()
    
    def read2(self, limit):
        import io
        result = io.BytesIO()
        result.write(self.buffer)
        try:
            while result.tell() < limit:
                result.write(next(self.generator))
        except StopIteration:
            pass
        return result.getvalue()
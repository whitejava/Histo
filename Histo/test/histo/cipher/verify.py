def main():
    for i in range(10000):
        print('Running', i)
        oneRun()

def oneRun():
    cipher = Cipher()
    data = randomData()
    code = encrypt(cipher, data)
    text = decrypt(cipher, code)
    assert data == text
    
def Cipher():
    from histo.cipher import Verify
    return Verify('md5')

def randomData():
    import random
    return randomBytes(int(random.gauss(100,100)))

def encrypt(cipher, data):
    print('Encrypting', reprBytes(data))
    encrypter = cipher.encrypt()
    return runCipher(encrypter, data)

def decrypt(cipher, data):
    print('Decrypting', reprBytes(data))
    decrypter = cipher.decrypt()
    return runCipher(decrypter, data)

def randomBytes(count):
    import random
    return bytes([random.randrange(256) for _ in range(count)])

def reprBytes(x):
    import base64
    return '%d %s' % (len(x), str(base64.b16encode(x), 'utf8'))

def runCipher(cipher, data):
    import io
    result = io.BytesIO()
    for a,b in runCipher2(cipher, data):
        if a is None:
            print('Finalize', reprBytes(b))
        else:
            print('Input', reprBytes(a))
            print('Output', reprBytes(b))
        result.write(b)
    result = result.getvalue()
    print('Result', reprBytes(result))
    return result

def runCipher2(cipher, data):
    import io
    result = io.BytesIO()
    for e in GaussSplit(data, 16, 16):
        code = cipher.update(e)
        result.write(code)
        yield (e, code)
    yield (None, cipher.final())

def GaussSplit(data, mean, sigma):
    import io
    stream = io.BytesIO(data)
    for e in Gauss(mean, sigma):
        if not e:
            continue
        read = stream.read(e)
        if not read:
            break
        yield read

def Gauss(mean, sigma):
    import random
    while True:
        yield int(abs(random.gauss(mean, sigma)))

if __name__ == '__main__':
    main()
def main():
    bundle = Bundle()
    from pclib import timetext
    name = timetext()
    testList(bundle)
    testWrite(bundle, name)
    testRead(bundle, name)

def Bundle():
    from histo.bundle import Mail
    return Mail('imap.gmail.com', 993, 'cpc.histo.d0', 'fae39928ef', 'cpc.histo.d0@gmail.com', 'histo@caipeichao.com')

def testList(bundle):
    print(bundle.list())

def testWrite(bundle, name):
    with bundle.open(name, 'wb') as f:
        for _ in range(100):
            f.write(b'a'*1024)

def testRead(bundle, name):
    with bundle.open(name, 'rb') as f:
        read = readAll(f)
        assert read == b'a'*100*1024

def readAll(file):
    import io
    result = io.BytesIO()
    while True:
        read = file.read(1024)
        if not read:
            break
        result.write(read)
    return result.getvalue()

if __name__ == '__main__':
    main()
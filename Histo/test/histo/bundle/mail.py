def main():
    bundle = Bundle()
    #testList(bundle)
    #testWrite(bundle)
    testRead(bundle)

def Bundle():
    from histo.bundle import Mail
    return Mail('imap.gmail.com', 993, 'cpc.histo.d0', 'fae39928ef', 'cpc.histo.d0@gmail.com', 'histo@caipeichao.com')

def testList(bundle):
    print(bundle.list())

def testWrite(bundle):
    with bundle.open('test1', 'wb') as f:
        for _ in range(100):
            f.write(b'a'*1024)

def testRead(bundle):
    with bundle.open('test1', 'rb') as f:
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
def main():
    bundle = Bundle()
    threads = []
    print('Expect output: 10')
    for i in range(10):
        threads.append(TestThread(bundle, i))
    from pclib import timer
    with timer():
        for e in threads:
            e.start()
        for e in threads:
            e.join()
        
def Bundle():
    from histo.bundle import Local, Limit
    from pclib import timetext
    return Limit(Local('D:\\%s-test-limit' % timetext()), 100000, 100000)

def TestThread(bundle, i):
    from threading import Thread
    return Thread(target = testWrite, args = (bundle,i))

def testWrite(bundle, i):
    with bundle.open(str(i), 'wb') as f:
        for _ in range(1000):
            f.write(b'a'*100)

if __name__ == '__main__':
    main()
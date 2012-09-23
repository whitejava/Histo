def main():
    bundle = Bundle()
    for _ in range(100):
        TestThread(bundle).start()

def Bundle():
    from histo.bundle import Local, Delay
    from pclib import timetext
    return Delay(Local('D:\\%s-test-delay' % timetext()), 0.5)

def TestThread(bundle):
    from threading import Thread
    return Thread(target = testAction, args = (bundle,))

def testAction(bundle):
    from pclib import timer
    with timer():
        with bundle.open('1', 'wb'):
            print('open')

if __name__ == '__main__':
    main()
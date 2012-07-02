from unittest import TestCase
from pctest import dumpdir
from autotemp import tempdir
from bundle import local
import random
import dfile

class test(TestCase):
    def test(self):
        for i in range(1):
            print('Test {}'.format(i))
            with tempdir() as temp:
                created = False
                bundle = local(temp,'{:04d}')
                partsize = random.randint(1,10)
                for i in range(20):
                    print('Operator {}'.format(i))
                    if created and random.randrange(2):
                        print('Read')
                        file = dfile.open(bundle, partsize, 'rb')
                        size = file.available()
                        for _ in range(100):
                            start = random.randrange(size)
                            end = random.randrange(size)
                            if start>end:
                                start,end = end,start
                            file.seek(start)
                            expect = getdata(start, end)
                            actual = file.read(end - start)
                            assert expect == actual
                        file.close()
                    else:
                        print('Write')
                        file = dfile.open(bundle, partsize, 'wb')
                        for _ in range(10):
                            start = file.tell()
                            length = random.randint(0,10)
                            end = start+length
                            data = getdata(start, end)
                            file.write(data)
                            created = True
                        file.close()

def getdata(start,end):
    return bytes([i%256 for i in range(start,end)])
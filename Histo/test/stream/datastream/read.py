from pctest import testcase,runins
from stream import datastream
import hex
import io

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(data, *k):
    data = hex.decode(data)
    stream = io.BytesIO(data)
    stream = datastream(stream)
    t = {'raw': lambda:stream.read(),
         'int': lambda:stream.readint(),
         'long': lambda:stream.readlong(),
         'bytes': lambda:stream.readbytes()}
    return runins(t,k)

data = \
'''
616263
raw
b'abc'

00000064
int
100

0000000000000064
long
100

00000003616263
bytes
b'abc'

00
int
error('unpack requires a bytes object of length 4',)

00000000
bytes
b''

000000ff00
bytes
AssertionError()

00000064000000000000006400000003616263
int
long
bytes
100-100-b'abc'
'''
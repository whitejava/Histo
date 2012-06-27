from pctest import testcase
import hex
import io
import stream
from stream import datastream

class test(testcase):
    def test_packint(self):
        self.batchtest(intdata, 1, stream._packint, (eval, hex.encode))
    def test_packlong(self):
        self.batchtest(longdata, 1, stream._packlong, (eval, hex.encode))
    def test_unpackint(self):
        self.batchtest(unintdata, 1, stream._unpackint, (eval, repr))
    def test_unpacklong(self):
        self.batchtest(unlongdata, 1, stream._unpacklong, (eval, repr))
    def test_write(self):
        self.batchtest(writedata, 2, write, (eval, str, hex.encode))
    def test_read(self):
        self.batchtest(readdata, 2, read, (hex.decode, str, repr))

def write(data, type):
    buffer = io.BytesIO()
    stream = datastream(buffer)
    {'none':stream.write,
     'int':stream.writeint,
     'long':stream.writelong,
     'bytes':stream.writebytes}[type](data)
    return buffer.getvalue()

def read(data, type):
    stream = datastream(io.BytesIO(data))
    return {'none':stream.read,
            'int':stream.readint,
            'long':stream.readlong,
            'bytes':stream.readbytes}[type]()

intdata = \
'''
0
00000000

1
00000001

100
00000064

-1
ffffffff

-2
fffffffe

9999999999999999
error('argument out of range',)

-9999999999999999
error('argument out of range',)

1.1
error('required argument is not an integer',)

0.1
error('required argument is not an integer',)

0.0
error('required argument is not an integer',)

None
error('required argument is not an integer',)
'''

longdata = \
'''
0
0000000000000000

1
0000000000000001

100
0000000000000064

256
0000000000000100

-1
ffffffffffffffff

-2
fffffffffffffffe

999999999999999999999999999999999
error('long too large to convert to int',)

-9999999999999999999999999999999
error('long too large to convert to int',)

1.1
error('required argument is not an integer',)

0.1
error('required argument is not an integer',)

0.0
error('required argument is not an integer',)

None
error('required argument is not an integer',)

[1]
error('required argument is not an integer',)
'''

unintdata = \
'''
bytes([0,0,0,1])
1

bytes([255,255,255,255])
-1

bytes([0,0,1,0])
256

bytes([0,0])
error('unpack requires a bytes object of length 4',)

bytes([0,1,2,3,4,5,6,7,8])
error('unpack requires a bytes object of length 4',)

[1,2,3,4]
TypeError("'list' does not support the buffer interface",)

(1,2,3,4)
TypeError("'tuple' does not support the buffer interface",)
'''

unlongdata = \
'''
bytes([0,0,0,0,0,0,0,0])
0

bytes([0,0,0,0,0,0,0,1])
1

bytes([255,255,255,255,255,255,255,255])
-1

bytes([0])
error('unpack requires a bytes object of length 8',)

[1,2,3,4,5,6,7,8]
TypeError("'list' does not support the buffer interface",)
'''

writedata = \
'''
b'abc'
none
616263

100
int
00000064

100
long
0000000000000064

b'abc'
bytes
00000003616263
'''

readdata = \
'''
616263
none
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
'''
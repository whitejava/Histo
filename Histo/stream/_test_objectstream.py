from pctest import testcase
import hex
import io
from stream import objectstream

class test(testcase):
    def test_write(self):
        self.batchtest(wdata, 1, write, (eval, hex.encode))
    def test_read(self):
        self.batchtest(rdata, 1, read, (hex.decode, repr))
    def test_writeread(self):
        self.batchtest(rwdata, 1, readwrite, (eval, repr))

def write(x):
    #Create buffer
    buffer = io.BytesIO()
    #Write object
    objectstream(buffer).write(x)
    #Return bytes
    return buffer.getvalue()

def read(x):
    return objectstream(io.BytesIO(x)).readobject()

def readwrite(x):
    return read(write(x))

wdata = \
'''
123
123

1.1
1.1

1.111111111111111111
1.111111111111111111

1111111111111111111111111111111111111111111111
1111111111111111111111111111111111111111111111

b'bytes'
b'bytes'

'string'
'string'

(1, 2, 3)
(1, 2, 3)

[1, 2, 3]
[1, 2, 3]

bytearray('bytearray')
bytearray('bytearray')

'\ucccc'
'\ucccc'

['complex', (1, b'123', 2, 3, 12.1, ['abc'])]
['complex', (1, b'123', 2, 3, 12.1, ['abc'])]
'''

rdata = \
'''
123
123

1.1
1.1

1.111111111111111111
1.111111111111111111

1111111111111111111111111111111111111111111111
1111111111111111111111111111111111111111111111

b'bytes'
b'bytes'

'string'
'string'

(1, 2, 3)
(1, 2, 3)

[1, 2, 3]
[1, 2, 3]

bytearray('bytearray')
bytearray('bytearray')

'\ucccc'
'\ucccc'

['complex', (1, b'123', 2, 3, 12.1, ['abc'])]
['complex', (1, b'123', 2, 3, 12.1, ['abc'])]
'''

rwdata = \
'''
123
123

1.1
1.1

1.111111111111111111
1.111111111111111111

1111111111111111111111111111111111111111111111
1111111111111111111111111111111111111111111111

b'bytes'
b'bytes'

'string'
'string'

(1, 2, 3)
(1, 2, 3)

[1, 2, 3]
[1, 2, 3]

bytearray('bytearray')
bytearray('bytearray')

'\ucccc'
'\ucccc'

['complex', (1, b'123', 2, 3, 12.1, ['abc'])]
['complex', (1, b'123', 2, 3, 12.1, ['abc'])]
'''
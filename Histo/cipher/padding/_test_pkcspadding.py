from pctest import testcase
from .pkcs7padding import encode, decode

class test(testcase):
    def test_encode(self):
        self.batchtest(goodencode, 2, encode, [eval, eval, repr])
    def test_decode(self):
        self.batchtest(gooddecode, 1, decode, [eval, repr])

goodencode = \
'''
b'a'
1
b'a\\x01'

b''
2
b'\\x02\\x02'

b'a'
2
b'a\\x01'

b'ab'
2
b'ab\\x02\\x02'

b''
3
b'\\x03\\x03\\x03'

b'a'
3
b'a\\x02\\x02'

b'ab'
3
b'ab\\x01'

b'abc'
3
b'abc\\x03\\x03\\x03'

bytearray([1,2,3])
3
bytearray(b'\\x01\\x02\\x03\\x03\\x03\\x03')

b''
0
ZeroDivisionError('integer division or modulo by zero',)

b''
1.1
TypeError("'float' object cannot be interpreted as an integer",)

b''
'a'
TypeError('unorderable types: str() < int()',)

b''
-1
ValueError('block size must be greater than zero.',)

b''
-2
ValueError('block size must be greater than zero.',)

'a'
3
TypeError("Can't convert 'bytes' object to str implicitly",)

[1]
3
TypeError('can only concatenate list (not "bytes") to list',)

b'\\xaa\\xbb\\xcc'
None
TypeError('unorderable types: NoneType() < int()',)
'''

gooddecode = \
'''
b'\\x03\\x03\\x03'
b''

b'\\xaa\\x02\\x02'
b'\\xaa'

b'\\xaa\\xbb\\x01'
b'\\xaa\\xbb'

bytearray(b'\\x01')
bytearray(b'')

bytearray(b'\\xaa\\x02\\x02')
bytearray(b'\\xaa')

b''
IndexError('index out of range',)

b'\\xff'
Exception('bad padding',)

b'\\x01\\x02'
Exception('bad padding',)

'a'
TypeError("bad operand type for unary -: 'str'",)

[1]
Exception('bad padding',)

b'\\xaa\\xbb\\x00'
Exception('bad padding',)
'''
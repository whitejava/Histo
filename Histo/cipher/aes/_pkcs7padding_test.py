from pctest import testcase
from ._pkcs7padding import encode, decode
from hex import hex

class test(testcase):
    def test_goodencode(self):
        self.batchtest(goodencode, 2, encode, [hex.decode, eval, hex.encode])
    def test_badencode(self):
        self.batchtest(badencode, 2, self.expecterror(encode), [eval, eval, repr])
    def test_gooddecode(self):
        self.batchtest(gooddecode, 1, decode, [hex.decode, hex.encode])
    def test_gooddecode2(self):
        self.batchtest(gooddecode2, 1, decode, [eval, repr])
    def test_baddecode(self):
        self.batchtest(baddecode, 1, self.expecterror(decode), [eval, repr])

goodencode = \
'''
aa
1
aa01


2
0202

aa
2
aa01

aabb
2
aabb0202


3
030303

aa
3
aa0202

aabb
3
aabb01

aabbcc
3
aabbcc030303
'''

gooddecode = \
'''
030303


aa0202
aa

aabb01
aabb
'''

gooddecode2 = \
'''
bytearray(b'\\x01')
bytearray(b'')

bytearray(b'\\xaa\\x02\\x02')
bytearray(b'\\xaa')
'''

badencode = \
'''
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

baddecode =\
'''
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
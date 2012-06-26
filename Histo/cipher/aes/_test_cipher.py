from pctest import testcase
from .cipher import cipher
from hex import hex

class test(testcase):
    def test_goodencodedecode(self):
        self.batchtest(goodencodedecode, 2, _encodedecode, (eval, eval, repr))
    def test_goodencode(self):
        self.batchtest(goodencode, 2, _encode, (lambda x:bytes(int(x)), lambda x:bytes(int(x)), lambda x:str(len(x))))
    def test_badencode(self):
        self.batchtest(badencode, 2, self.expecterror(_encode), (eval, eval, repr))
    def test_baddecode(self):
        self.batchtest(baddecode, 2, self.expecterror(_decode), (eval, eval, repr))

def _encodedecode(key, data):
    #Code
    code = _encode(key, data)
    #Print code
    print(hex.encode(code))
    #Encode and decode
    return _decode(key, code)

def _encode(key, data):
    #Return code
    return cipher(key).encode(data)

def _decode(key, data):
    #Return text
    return cipher(key).decode(data)

goodencodedecode = \
'''
b'1'*32
b''
b''

b'1'*32
b'a'
b'a'

b'1'*32
b'abc'
b'abc'

b'1'*32
b'0123456789abcdef'
b'0123456789abcdef'

b'1'*24
b'0123'
b'0123'

b'1'*16
b'abc'
b'abc'

'1'*32
b'abc'
b'abc'

'1'*16
b'abc'
b'abc'

'1'*24
b'abc'
b'abc'
'''

goodencode = \
'''
16
1
32

16
2
32

16
16
48

32
1
32

32
2
32

32
32
64
'''

badencode = \
'''
b'0'*64
b'abc'
ValueError('AES key must be either 16, 24, or 32 bytes long',)

bytearray([1]*32)
b'abc'
TypeError('argument 1 must be read-only pinned buffer, not bytearray',)

b'0'*32
bytearray([1,2,3])
TypeError('argument must be read-only pinned buffer, not bytearray',)

[1]*32
b'abc'
TypeError("'list' does not support the buffer interface",)

b'0'*32
[1,2,3]
TypeError('can only concatenate list (not "bytes") to list',)

'0'*33
b'abc'
ValueError('AES key must be either 16, 24, or 32 bytes long',)

tuple([1]*32)
b'a'
TypeError("'tuple' does not support the buffer interface",)

1.5
b'abc'
TypeError("'float' does not support the buffer interface",)

b'0'*32
1.5
TypeError("object of type 'float' has no len()",)

b'1'*32
'123'
TypeError("Can't convert 'bytes' object to str implicitly",)
'''

baddecode = \
'''
b'1'*32
b'0'*64
Exception('bad padding',)

bytearray([1])*32
b'a'*32
TypeError('argument 1 must be read-only pinned buffer, not bytearray',)

b'1'*32
bytearray([1])
TypeError('argument 3 must be read-only pinned buffer, not bytearray',)

b'1'*32
b'abc'
ValueError('IV must be 16 bytes long',)

None
b'abc'
TypeError("'NoneType' does not support the buffer interface",)

b'1'*32
None
TypeError("'NoneType' object is not subscriptable",)

b'1'*32
b'a'*20
ValueError('Input strings must be a multiple of 16 in length',)

b'1'*32
b''
IndexError('index out of range',)
'''
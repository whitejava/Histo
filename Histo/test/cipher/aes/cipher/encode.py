from pctest import testcase
from cipher.aes import cipher

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(key,data):
    key = eval(key)
    data = eval(data)
    result = cipher(key).encode(data)
    return repr(len(result))

data = \
'''
b'0'*16
b'0'*1
32

b'0'*16
b'0'*2
32

b'0'*16
b'0'*16
48

b'0'*24
b'0'*16
48

b'0'*32
b'0'*1
32

b'0'*32
b'0'*2
32

b'0'*32
b'0'*32
64

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
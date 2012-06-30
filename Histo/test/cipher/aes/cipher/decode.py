from pctest import testcase
from cipher.aes import cipher
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(key,code):
    key = eval(key)
    code = eval(code)
    return hex.encode(cipher(key).decode(code))

data = \
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
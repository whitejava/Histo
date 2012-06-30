from pctest import testcase
from cipher.padding import pkcs7padding
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(data):
    data = eval(data)
    result = pkcs7padding.decode(data)
    return '{},{}'.format(type(result).__name__, hex.encode(result))

data = \
'''
b'\\x03\\x03\\x03'
bytes,

b'\\xaa\\x02\\x02'
bytes,aa

b'\\xaa\\xbb\\x01'
bytes,aabb

bytearray(b'\\x01')
bytearray,

bytearray(b'\\xaa\\x02\\x02')
bytearray,aa

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
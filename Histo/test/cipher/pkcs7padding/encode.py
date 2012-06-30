from pctest import testcase
from cipher.padding import pkcs7padding
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(data, padsize):
    type,data = data.split(',')
    type = eval(type)
    data = hex.decode(data)
    data = type(data)
    padsize = eval(padsize)
    result = pkcs7padding.encode(data, padsize)
    return '{},{}'.format(__builtins__['type'](result).__name__, hex.encode(result))

data = \
'''
bytes,aa
1
bytes,aa01

bytes,
2
bytes,0202

bytes,aa
2
bytes,aa01

bytes,aabb
2
bytes,aabb0202

bytes,
3
bytes,030303

bytes,aa
3
bytes,aa0202

bytes,aabb
3
bytes,aabb01

bytes,aabbcc
3
bytes,aabbcc030303

bytearray,010203
3
bytearray,010203030303

bytes,
0
ZeroDivisionError('integer division or modulo by zero',)

bytes,
1.1
TypeError("'float' object cannot be interpreted as an integer",)

bytes,
'a'
TypeError('unorderable types: str() < int()',)

bytes,
-1
ValueError('block size must be greater than zero.',)

bytes,
-2
ValueError('block size must be greater than zero.',)

str,aa
3
TypeError("Can't convert 'bytes' object to str implicitly",)

list,01
3
TypeError('can only concatenate list (not "bytes") to list',)

bytes,aabbcc
None
TypeError('unorderable types: NoneType() < int()',)
'''
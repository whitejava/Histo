from pctest import testcase
from stream import _unpacklong as unpacklong

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(input):
    input = eval(input)
    return unpacklong(input)

data = \
'''
bytes([0,0,0,0,0,0,0,0])
0

bytes([0,0,0,0,0,0,0,1])
1

bytes([255,255,255,255,255,255,255,255])
-1

bytes([127,255,255,255,255,255,255,255])
9223372036854775807

bytes([0])
error('unpack requires a bytes object of length 8',)

[1,2,3,4,5,6,7,8]
TypeError("'list' does not support the buffer interface",)
'''
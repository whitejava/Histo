from pctest import testcase
from stream import _unpackint as unpackint
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(input):
    input = eval(input)
    return unpackint(input)

data = \
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
from pctest import testcase
from stream import _packint as packint
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(input):
    input = eval(input)
    result = packint(input)
    result = hex.encode(result)
    return result

data = \
'''
0
00000000

1
00000001

100
00000064

-1
ffffffff

-2
fffffffe

9999999999999999
error('argument out of range',)

-9999999999999999
error('argument out of range',)

1.1
error('required argument is not an integer',)

0.1
error('required argument is not an integer',)

0.0
error('required argument is not an integer',)

None
error('required argument is not an integer',)
'''
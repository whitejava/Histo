from pctest import testcase
from stream import _packlong as packlong
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(input):
    input = eval(input)
    result = packlong(input)
    result = hex.encode(result)
    return result

data = \
'''
0
0000000000000000

1
0000000000000001

100
0000000000000064

256
0000000000000100

-1
ffffffffffffffff

-2
fffffffffffffffe

999999999999999999999999999999999
error('long too large to convert to int',)

-9999999999999999999999999999999
error('long too large to convert to int',)

1.1
error('required argument is not an integer',)

0.1
error('required argument is not an integer',)

0.0
error('required argument is not an integer',)

None
error('required argument is not an integer',)

[1]
error('required argument is not an integer',)
'''
from pctest import testcase
from stream import transferstream
import io

class test(testcase):
    def test_transferstream(self):
        self.batchtest(transferdata, 4, transfer, (str, eval, str, eval, repr))

def transfer(input, indata, output, chunksize):
    t = {'BytesIO': io.BytesIO, 'StringIO': io.StringIO}
    output = t[output]()
    transferstream(t[input](indata), output, chunksize)
    return output.getvalue()

transferdata = \
'''
BytesIO
b'abc'
BytesIO
2
b'abc'

BytesIO
b'abc'
BytesIO
-2
b'abc'

StringIO
'abcde'
StringIO
-3
'abcde'

BytesIO
b'abc'
BytesIO
1.1
TypeError("integer argument expected, got 'float'",)

StringIO
'abcd'
StringIO
2
'abcd'

BytesIO
b'abcd'
StringIO
2
TypeError("string argument expected, got 'bytes'",)

StringIO
'abcd'
BytesIO
2
TypeError("'str' does not support the buffer interface",)
'''

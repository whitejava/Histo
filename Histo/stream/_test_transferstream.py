from pctest import testcase
import stream
import io

class test(testcase):
    def test_copy(self):
        self.batchtest(copydata, 4, copy, (str, eval, str, eval, repr))

def copy(input, indata, output, chunksize):
    t = {'BytesIO': io.BytesIO, 'StringIO': io.StringIO}
    output = t[output]()
    stream.copy(t[input](indata), output, chunksize)
    return output.getvalue()

copydata = \
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

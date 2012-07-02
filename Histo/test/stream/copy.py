from pctest import testcase
import stream
import hex
import io

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(input, indata, output, chunksize):
    indata = eval(indata)
    chunksize = eval(chunksize)
    t = {'BytesIO': io.BytesIO, 'StringIO': io.StringIO}
    output = t[output]()
    stream.copy(t[input](indata), output, chunksize)
    return repr(output.getvalue())

data = \
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
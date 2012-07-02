from pctest import testcase,runins
from stream import datastream
import hex
import io

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(*k):
    buffer = io.BytesIO()
    stream = datastream(buffer)
    t = {'write': lambda x:stream.write(eval(x)),
         'int': lambda x:stream.writeint(eval(x)),
         'long': lambda x:stream.writelong(eval(x)),
         'bytes': lambda x:stream.writebytes(eval(x)),
         'buffer': lambda:hex.encode(buffer.getvalue())}
    return runins(t,k)

data = \
'''
write b'abc'
buffer
int 100
buffer
long 100
buffer
bytes b'abc'
buffer
616263-61626300000064-616263000000640000000000000064-61626300000064000000000000006400000003616263
'''
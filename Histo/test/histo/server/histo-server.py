from pctest import testcase
import io
from . import server
from autotemp import tempfile
import hex

class test(testcase):
    def testaccept(self):
        self.batchtest(acceptdata, 1, accept, (hex.decode, repr))

def accept(source):
    with tempfile('server-test-') as temp:
        ac = server._accept(io.BytesIO(source), temp)
        with open(temp, 'rb') as f: data = f.read()
        return (ac[0], ac[1], data)
        
acceptdata = \
'''
800358060000006e6f726d616c71002e8003284ddc074b064b1a4b144b264b004b007471002e80034b102e54686973206973206120746573742e0a
((2012, 6, 26, 20, 38, 0, 0), 'normal', b'This is a test')
'''
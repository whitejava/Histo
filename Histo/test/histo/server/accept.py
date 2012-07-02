from pctest import testcase
from autotemp import tempfile
import histo.server
import hex
import io

class test(testcase):
    def test(self):
        self.bulktest(acceptdata, func)

def func(source):
    source = hex.decode(source)
    source = io.BytesIO(source)
    with tempfile('server-test-') as temp:
        ac = histo.server._accept(source, temp)
        with open(temp, 'rb') as f: data = f.read()
        return (ac[0], ac[1], data)

acceptdata = \
'''
8003284ddc074b064b1a4b144b264b004b007471002e800358060000006e6f726d616c71002e80034b102e54686973206973206120746573742e0a
((2012, 6, 26, 20, 38, 0, 0), 'normal', b'This is a test.\\n')
'''
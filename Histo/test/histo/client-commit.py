from pctest import testcase
from pctest import gettestfile
import hex
import io
from histo.client import commitprevious

class test(testcase):
    def test(self):
        self.batchtest(data, 1, commit, (str, hex.encode))

def commit(filename):
    stream = io.BytesIO()
    commitprevious(gettestfile(filename), stream)
    return stream.getvalue()

data = \
'''
201206262038normal.rar
8003284ddc074b064b1a4b144b264b004b007471002e800358060000006e6f726d616c71002e80034b102e54686973206973206120746573742e0a

201206262038nonexist.rar
OSError(2, 'No such file or directory')
'''
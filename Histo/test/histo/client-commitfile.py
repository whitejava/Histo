from pctest import testcase
from pctest import gettestfile
import hex
import io
from histo.client import commitfile

class test(testcase):
    def test(self):
        self.batchtest(data, 3, commit, (eval, str, lambda x:gettestfile(x), hex.encode))

def commit(time, name, filename):
    stream = io.BytesIO()
    commitfile(name, gettestfile(filename), stream, time = time)
    return stream.getvalue()

data = \
'''
(2012,6,26,20,38,0,0)
normal
test.txt
8003284ddc074b064b1a4b144b264b004b007471002e800358060000006e6f726d616c71002e80034b102e54686973206973206120746573742e0a

None
use now
test.txt
80034e2e80035807000000757365206e6f7771002e80034b102e54686973206973206120746573742e0a

None
non exist
201206262038nonexist.rar
OSError(2, 'No such file or directory')
'''
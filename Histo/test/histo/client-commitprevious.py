from pctest import testcase, gettestfile
from histo.client import commitprevious
import hex
import io

class test(testcase):
    def test(self):
        self.batchtest(data, 1, commit, (lambda x:gettestfile(x), hex.encode))

def commit(filename):
    buffer = io.BytesIO()
    commitprevious(filename, buffer)
    return buffer.getvalue()

data = \
'''
201206262038normal.rar
8003284ddc074b064b1a4b144b264b004b007471002e800358060000006e6f726d616c71002e80034b102e54686973206973206120746573742e0a

201206262038nonexist.rar
OSError(2, 'No such file or directory')

badfilename
ValueError("invalid literal for int() with base 10: 'badf'",)
'''
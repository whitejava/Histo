from pctest import testcase
import hex
import os
import io
from histo import client

class test(testcase):
    def test_cut(self):
        self.batchtest(cutdata, 2, client._cut, (eval,eval,repr))
    def test_resolvefilename(self):
        self.batchtest(resolvedata, 1, client._resolvefilename, (eval, repr))
    def test_commit(self):
        self.batchtest(commitdata, 1, commit, (gettestfile, hex.encode))

def gettestfile(filename):
    return os.path.join(os.path.dirname(__file__), 'histo-client', filename)

def commit(filename):
    stream = io.BytesIO()
    client.commitprevious(filename, stream)
    return stream.getvalue()

cutdata = \
'''
'0123456789'
[2,3]
['01', '234']

'0123'
[]
[]

'abc'
[9]
['abc']

'123456789'
[2,100,10]
['12', '3456789', '']

[1,2,3,4,5,6,7]
[2,3,1]
TypeError('initial_value must be str or None, not list',)

b'abc'
[1,2]
TypeError('initial_value must be str or None, not bytes',)

'1234567890'
[0,1,2,3,4]
['', '1', '23', '456', '7890']

None
[1]
['']
'''

resolvedata = \
'''
'201206262245normal.rar'
((2012, 6, 26, 22, 45, 0, 0), 'normal')

'201206262245_123digit.rar'
((2012, 6, 26, 22, 45, 0, 0), '123digit')

'201206262245.rar'
((2012, 6, 26, 22, 45, 0, 0), '')

'201206262245.tar.gz'
((2012, 6, 26, 22, 45, 0, 0), '.ta')

'123'
ValueError("invalid literal for int() with base 10: ''",)

123
AttributeError("'int' object has no attribute 'rfind'",)

None
AttributeError("'NoneType' object has no attribute 'rfind'",)

b'201206262245.tar.gz'
TypeError('initial_value must be str or None, not bytes',)
'''

commitdata = \
'''
201206262038normal.rar
800358060000006e6f726d616c71002e8003284ddc074b064b1a4b144b264b004b007471002e80034b102e54686973206973206120746573742e0a

bad.rar
ValueError("invalid literal for int() with base 10: 'bad.'",)

201206262038nonexist.rar
OSError(2, 'No such file or directory')
'''
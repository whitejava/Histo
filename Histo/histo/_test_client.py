from pctest import testcase
import hex
import os
import io
from . import client

class test(testcase):
    def test_packint(self):
        self.batchtest(intdata, 1, client._packint, (eval, hex.encode))
    def test_packlong(self):
        self.batchtest(longdata, 1, client._packlong, (eval, hex.encode))
    def test_cut(self):
        self.batchtest(cutdata, 2, client._cut, (eval,eval,repr))
    def test_resolvefilename(self):
        self.batchtest(resolvedata, 1, client._resolvefilename, (eval, repr))
    def test_transferstream(self):
        self.batchtest(transferdata, 4, transfer, (str, eval, str, eval, repr))
    def test_commit(self):
        self.batchtest(commitdata, 1, commit, (gettestfile, hex.encode))

def gettestfile(filename):
    return os.path.join(os.path.dirname(__file__), '_test_commit', filename)

def commit(filename):
    output = io.BytesIO()
    client.commit(filename, output)
    return output.getvalue()

def transfer(input, indata, output, chunksize):
    t = {'BytesIO': io.BytesIO, 'StringIO': io.StringIO}
    output = t[output]()
    client._transferstream(t[input](indata), output, chunksize)
    return output.getvalue()

intdata = \
'''
0
00000000

1
00000001

100
00000064

-1
ffffffff

-2
fffffffe

9999999999999999
error('argument out of range',)

-9999999999999999
error('argument out of range',)

1.1
error('required argument is not an integer',)

0.1
error('required argument is not an integer',)

0.0
error('required argument is not an integer',)

None
error('required argument is not an integer',)
'''

longdata = \
'''
0
0000000000000000

1
0000000000000001

100
0000000000000064

256
0000000000000100

-1
ffffffffffffffff

-2
fffffffffffffffe

999999999999999999999999999999999
error('long too large to convert to int',)

-9999999999999999999999999999999
error('long too large to convert to int',)

1.1
error('required argument is not an integer',)

0.1
error('required argument is not an integer',)

0.0
error('required argument is not an integer',)

None
error('required argument is not an integer',)

[1]
error('required argument is not an integer',)
'''

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

commitdata = \
'''
201206262038normal.rar
000000066e6f726d616c00000007000007dc000000060000001a00000014000000260000000000000000000000000000001054686973206973206120746573742e0a

bad.rar
ValueError("invalid literal for int() with base 10: 'bad.'",)

201206262038nonexist.rar
OSError(2, 'No such file or directory')
'''
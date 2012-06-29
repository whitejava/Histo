from pctest import testcase
import hex

class test(testcase):
    def test(self):
        self.batchtest(data, 1, hex.encode, (eval, repr))

data = \
'''
b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
'303132333435363738396162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464748494a4b4c4d4e4f505152535455565758595a'

b''
''

bytearray([1,2,3])
'010203'

'abc'
ValueError("Unknown format code 'x' for object of type 'str'",)

[1,2,3]
'010203'

(1,2,3)
'010203'

[300,400]
'12c190'

None
TypeError("'NoneType' object is not iterable",)
'''
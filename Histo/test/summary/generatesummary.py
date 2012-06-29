from pctest import testcase, gettestfile
from summary import generate_summary as generatesummary

class test(testcase):
    def test(self):
        self.batchtest(data, 2, generatesummary, (str, lambda x:gettestfile(x), repr))

data = \
'''
test
normal.rar
('test', ('rar', None, (('a', (('1', None), ('3', None), ('2', None))),)))

test
bad.rar
('test', ('rar', 'extract error 10', ()))

test
encrypt.rar
('test', ('rar', 'extract error 1', (('a', ()),)))

test
'embed.rar'
('test', ('rar', None, (('embed1.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed2.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed3.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))))))
'''
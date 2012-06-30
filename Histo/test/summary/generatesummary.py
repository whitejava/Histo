from pctest import testcase, gettestfile
from summary import generatesummary

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(name, filename):
    filename = gettestfile(filename, source = 'archive')
    return repr(generatesummary(name, filename))

data = \
'''
test
normal.rar
('test', ('rar', None, (('a', (('1', None), ('3', None), ('2', None))),)))

test
bad.rar
('test', ('rar', "extracterror('no file to extract')", ()))

test
encrypt.rar
('test', ('rar', "extracterror('warning')", (('a', ()),)))

test
embed.rar
('test', ('rar', None, (('embed1.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed2.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed3.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))))))
'''
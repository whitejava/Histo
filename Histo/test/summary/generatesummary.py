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
bad.rar
('test', ('rar', "extracterror('no file to extract')", ()))

test
bad.tar
('test', ('tar', "extracterror('bad tar file')", ()))

test
bad.zip
('test', ('zip', "extracterror('zipfile not found')", ()))

test
contain space.rar
('test', ('rar', None, (('a', (('1', None), ('3', None), ('2', None))),)))

test
embed.rar
('test', ('rar', None, (('embed1.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed2.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed3.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))))))

test
encrypt.rar
('test', ('rar', "extracterror('warning')", (('a', ()),)))

test
encrypt.zip
('test', ('zip', "extracterror('fail read password')", ()))

test
normal.rar
('test', ('rar', None, (('a', (('1', None), ('3', None), ('2', None))),)))

test
normal.tar
('test', ('tar', None, (('a', (('b', None), ('d', None), ('c', None))),)))

test
normal.tar.bz2
('test', ('tar', None, (('a', (('b', None), ('d', None), ('c', None))),)))

test
normal.tar.gz
('test', ('tar', None, (('a', (('1', None), ('3', None), ('2', None))),)))

test
normal.zip
('test', ('zip', None, (('a', (('b', None), ('d', None), ('c', None))),)))

test
nonexist.rar
('test', ('rar', "extracterror('no file to extract')", ()))

test
nonexist.tar
('test', ('tar', "extracterror('bad tar file')", ()))

test
nonexist.zip
('test', ('zip', "extracterror('zipfile not found')", ()))

test
nonexist
('test', None)
'''
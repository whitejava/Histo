from pctest import testcase,gettestfile
from summary import _extractarchive as extractarchive
from autotemp import tempdir
from listfiles import listfiles

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(type,filename):
    filename = gettestfile(filename, source = 'archive')
    with tempdir('extract-test-') as temp:
        extractarchive(type, filename, temp)
        return repr(listfiles(temp))

data = \
'''
rar
bad.rar
extracterror('no input file')

tar
bad.tar
extracterror('no input file')

zip
bad.zip
extracterror('no input file')

rar
contain space.rar
['/a', '/a/1', '/a/3', '/a/2']

rar
embed.rar
['/embed1.rar', '/embed2.rar', '/embed3.rar']

rar
encrypt.rar
extracterror('warning')

zip
encrypt.zip
extracterror('fail read password')

rar
normal.rar
['/a', '/a/1', '/a/3', '/a/2']

tar
normal.tar
['/a', '/a/b', '/a/d', '/a/c']

tar
normal.tar.bz2
['/a', '/a/b', '/a/d', '/a/c']

tar
normal.tar.gz
['/a', '/a/1', '/a/3', '/a/2']

zip
normal.zip
['/a', '/a/b', '/a/d', '/a/c']

rar
nonexist.rar
extracterror('no input file')

zip
nonexist.zip
extracterror('no input file')

tar
nonexist.tar
extracterror('no input file')
'''
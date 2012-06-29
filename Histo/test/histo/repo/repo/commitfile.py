from pctest import testcase, gettestfile
from autotemp import tempdir
from histo._repo import repo
from histo._repo import _securedfile
import hex
import os

class test(testcase):
    def test(self):
        self.batchtest(data, 4, commit, (eval, lambda x:gettestfile(x), eval, eval, str))

def commit(key, filename, name, time):
    with tempdir('repo-test-') as temp:
        with repo(temp, key) as f:
            f.commitfile(filename, name, time)
            return dumprepo(temp, key)

def dumprepo(root, key):
    index = _securedfile(os.path.join(root,'index'), 'i{:06d}', 1024*1024, key, 'rb')
    data = _securedfile(os.path.join(root,'data'), 'd{:08d}', 10*1024*1024, key, 'rb')
    with index as f1, data as f2:
        return '{},{}'.format(hex.encode(f1.read()),hex.encode(f2.read()))

data = \
'''
b'0'*32
normal.rar
'name'
(2012, 6, 29, 22, 49, 0, 0)
00,00
'''
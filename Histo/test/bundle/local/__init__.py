from pctest import testcase,dumpdir,runins
from bundle import local
from autotemp import tempdir
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(*k):
    with tempdir() as temp:
        bundle = local(temp, '{:04}')
        t = {'dump':lambda x,y:bundle.dump(eval(x),hex.decode(y)),
             'load':lambda x:bundle.load(eval(x)),
             'exists':lambda x:bundle.exists(eval(x)),
             'dumpdir':lambda:dumpdir(temp)}
        return runins(t,k)

data = \
'''
dump 0 aabb
load 0
exists 0
exists 1
dump 1 ccdd
exists 1
load 0
load 1
dump 0 bbcc
exists 0
load 0
dump 1 ddcc
exists 1
exists 2
load 1
load 2
dumpdir
None-b'\\xaa\\xbb'-True-False-None-True-b'\\xaa\\xbb'-b'\\xcc\\xdd'-None-True-b'\\xbb\\xcc'-None-True-False-b'\\xdd\\xcc'-IOError(2, 'No such file or directory')-0000:bbcc,0001:ddcc
'''
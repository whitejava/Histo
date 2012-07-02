from pctest import testcase,dumpdir,runins,createfiles
from bundle import local
from autotemp import tempdir
import hex
import os

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(subdir, *k):
    subdir = eval(subdir)
    with tempdir() as temp:
        temp = os.path.join(temp, *subdir)
        bundle = local(temp, '{:04}')
        t = {'dump':lambda x,y:bundle.dump(eval(x),hex.decode(y)),
             'load':lambda x:hex.encode(bundle.load(eval(x))),
             'exists':lambda x:bundle.exists(eval(x)),
             'dumpdir':lambda:dumpdir(temp),
             'createfiles': lambda x:createfiles(temp,x)}
        return runins(t,k)

data = \
'''
[]
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
aabb-True-False-True-aabb-ccdd-True-bbcc-True-False-ddcc-IOError(2, 'No such file or directory')-0000:bbcc,0001:ddcc

['nonexists']
dump 0 aabb
load 0
?

[]
createfiles 0000:<folder>
exists 0
dump 0 aabb
load 0
exists 0
False-IOError(13, 'Permission denied')-IOError(13, 'Permission denied')-False
'''
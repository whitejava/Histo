from pctest import testcase
from autotemp import tempdir
from summary import _foldersummary as foldersummary
import os

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(files):
    #In temp dir
    with tempdir('sumf-test-') as temp:
        #Create files
        for file in eval(files):
            path = os.path.join(temp,file)
            folder = os.path.dirname(path)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(path,'wb') as f: pass
        #Return summary
        return repr(foldersummary(temp))

data = \
'''
['a/b/c/d/e','f/g','f/h/i']
(('f', (('g', None), ('h', (('i', None),)))), ('a', (('b', (('c', (('d', (('e', None),)),)),)),)))

['a/b']
(('a', (('b', None),)),)

['a']
(('a', None),)

[]
()
'''
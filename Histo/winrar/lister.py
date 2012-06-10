from tempdir.tempdir import tempdir
import os

class lister:
    def __init__(self,rar):
        self._rar = rar
    
    def list(self):
        r = []
        with tempdir(prefix='rarlist') as d:
            if self._extract_rar(self._rar, d):
                li = self._list_dir(d)
                for e in li:
                    r.append(e)
                    if self._is_file(d,e):
                        for e2 in lister(e).list():
                            r.append('>>'.join(e,e2))
    
    def _list_dir(self,d):
        r = []
        for dirname, dirnames, filenames in os.walk('.'):
            for e in dirnames:
                r.append(e[len(d)+1:])
            for e in filenames:
                r.append(e[len(d)+1:])
        return r
    
    def _is_file(self,root,file):
        return os.path.isfile(os.path.join(root,file))
    
    def _extract_dir(self,d):
        'winrar e {} -ibck'
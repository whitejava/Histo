from tempdir.tempdir import tempdir
import os

class lister:
    def __init__(self,rar):
        self._rar = rar
        self._archive_extensions = 'RAR,ZIP,7Z,ACE,ARJ,BZ2,CAB,GZ,ISO,JAR,LZH,TAR,UUE,Z'.split(',')

    def list(self):
        r = []
        with tempdir(prefix='rarlist') as d:
            if self._extract_rar(self._rar, d):
                li = self._list_dir(d)
                for e in li:
                    r.append(e)
                    f = os.path.join(d,e)
                    if self._is_archive_file(f):
                        for e2 in lister(f).list():
                            r.append('>>'.join([e,e2]))
        return r
    
    def _list_dir(self,d):
        r = []
        for dirname, dirnames, filenames in os.walk(d):
            for e in dirnames:
                x=os.path.join(dirname,e)
                r.append(x[len(d)+1:])
            for e in filenames:
                x=os.path.join(dirname,e)
                r.append(x[len(d)+1:])
        return r
    
    def _extract_rar(self,rar,d):
        import subprocess
        subprocess.call(['winrar','x',rar,'-ibck','-inul',d+'\\'])
        return True
    
    def _is_archive_file(self,f):
        if not os.path.isfile(f):
            return False
        ext = f.split('.')[-1].upper()
        return ext in self._archive_extensions
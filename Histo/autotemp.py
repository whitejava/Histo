import tempfile as otemp
import os
import shutil
import stat

__all__ = ['tempfile','tempdir']

class tempfile:
    def __init__(self, prefix = 'tmp', suffix = '', dir = None):
        self._prefix = prefix
        self._suffix = suffix
        self._dir = dir
    
    def __enter__(self):
        self._temp = otemp.NamedTemporaryFile('wb', suffix = self._suffix, prefix=self._prefix, dir=self._dir, delete=False)
        self._temp.close()
        return self._temp.name
    
    def __exit__(self, *k):
        os.remove(self._temp.name)

def _forceremove(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

class tempdir:
    def __init__(self, prefix = 'tmp', suffix = '', dir = None):
        self._prefix = prefix
        self._suffix = suffix
        self._dir = dir
    
    def __enter__(self):
        self._temp = otemp.mkdtemp(self._suffix, self._prefix, self._dir)
        return self._temp
    
    def __exit__(self, *k):
        shutil.rmtree(self._temp, onerror = _forceremove)
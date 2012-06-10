import tempfile
import shutil
import os

class tempdir:
    def __init__(self,suffix="",prefix="",dir=None):
        self._suffix = suffix
        self._prefix = prefix
        self._dir= dir
    
    def __enter__(self):
        self._temp = tempfile.mkdtemp(self._suffix, self._prefix, self._dir)
        return self._temp
    
    def __exit__(self,*k):
        shutil.rmtree(self._temp, True)
        if os.path.exists(self._temp):
            raise Exception('cannot delete temp dir')
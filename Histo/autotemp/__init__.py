import tempfile as otemp
import os
import shutil

class tempfile:
    def __init__(self, prefix = 'tmp', suffix = '', dir = None):
        self._prefix = prefix
        self._suffix = suffix
        self._dir = dir
    
    def __enter__(self):
        self._temp = otemp.mktemp(self._suffix, self._prefix, self._dir)
        return self._temp
    
    def __exit__(self, *k):
        os.remove(self._temp)

class tempdir:
    def __init__(self, prefix = 'tmp', suffix = '', dir = None):
        self._prefix = prefix
        self._suffix = suffix
        self._dir = dir
    
    def __enter__(self):
        self._temp = otemp.mkdtemp(self._suffix, self._prefix, self._dir)
        return self._temp
    
    def __exit__(self, *k):
        shutil.rmtree(self._temp)
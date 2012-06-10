from winrar.lister import lister
from .index.writer import writer as index_writer

class repo:
    def __init__(self,index,data):
        self._index = index
        self._data = data
    
    def commit_rar(self, rar, name, commit_time = None):
        start = self._data.tell()
        self._write_data(file=rar)
        end = self._data.tell()
        index = self._make_index(rar=rar,commit_time=commit_time,name=name,range=(start,end))
        with index_writer(self._index) as f:
            f.write(index)
    
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        pass
    
    def _write_data(self,file,chunk_size = 512*1024):
        with open(file,'rb') as f:
            while True:
                read = f.read(chunk_size)
                if not read:
                    break
                self._data.write(read)
    
    def _make_index(self,rar,commit_time,name,range):
        last_modify = self._get_last_modify(rar)
        files = self._list_rar(rar)
        c = (('version',0),
             ('commit_time', self._totuple(commit_time)),
             ('name', name),
             ('last_modify', self._totuple(last_modify)),
             ('range', range),
             ('files', tuple(files)))
        return c
    
    def _get_last_modify(self,file):
        import os
        import datetime
        return datetime.datetime.fromtimestamp(os.path.getmtime(file))
    
    def _totuple(self,t):
        return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

    def _list_rar(self,rar):
        return lister(rar).list()
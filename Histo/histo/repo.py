from .index.writer import writer as index_writer

def _copy(input, output):
    

class repo:
    def __init__(self, index_output, data_output):
        self._index_output = index_output
        self._data_output = data_output
    
    def commit_file(self, filename, commit_name, commit_time = None):
        start = self._data_output.tell()
        _copy(filename, self._data_output)
        end = self._data_output.tell()
        index = _make_index(commit_time = commit_time,
                            commit_name = commit_name,
                            summary = summary,
                            range = (start, end))
    
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
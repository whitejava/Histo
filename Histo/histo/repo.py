from winrar.lister import lister

class repo:
    def __init__(self,index,data):
        self._index = index
        self._data = data
    
    def commit_rar(self, rar, commit_time = None):
        start = self._data.tell()
        self._write_data(file=rar)
        end = self._data_tell()
        index = self._make_index(rar=rar,commit_time=commit_time,range=(start,end))
        self._index.write(index)
    
    def _write_data(self,file,chunk_size = 512*1024):
        with open(file,'rb') as f:
            while True:
                read = f.read(chunk_size)
                if not read:
                    break
                self._data.write(read)
    
    def _make_index(self,rar,commit_time,range):
        last_modify = self._get_last_modify(rar)
        files = self._list_rar(rar)
        c = [('version',0),
             ('commit_time', self._totuple(commit_time)),
             ('last_modify', self._totuple(last_modify)),
             ('range', range),
             ('files', files)]
        return c
    
    def _totuple(self,t):
        return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)
def _copy(input, output, chunk_size = 512*1024):
    while True:
        read = input.read(chunk_size)
        if not read:
            break
        output.write(read)

def _convert_time_to_tuple(t):
    return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

def _get_last_modify(filename):
    import os
    import datetime
    return datetime.datetime.fromtimestamp(os.path.getmtime(filename))

def _make_index(version,time,name,last_modify,range,summary):
    return (('version',version),
            ('time',time),
            ('name',name),
            ('last-modify',last_modify),
            ('range',range),
            ('summary',summary))

def _get_now():
    import datetime
    return datetime.datetime.now()

def _get_now_tuple():
    return _convert_time_to_tuple(_get_now())

def _get_last_modify_tuple(filename):
    return _convert_time_to_tuple(_get_last_modify(filename))

class repo:
    def __init__(self, index_output, data_output):
        self._index_output = index_output
        self._data_output = data_output
    
    def commit_file(self, filename, name, summary, time = None):
        if time == None:
            time = _get_now_tuple()
        start = self._data_output.tell()
        self._write_data(filename)
        end = self._data_output.tell()
        index = _make_index(version = 0,
                            time = time,
                            name = name,
                            last_modify = _get_last_modify_tuple(filename),
                            range = (start, end),
                            summary = summary)
        self._write_index(index)
    
    def _write_data(self, filename):
        with open(filename, 'rb') as f:
            _copy(f, self._data_output)

    def _write_index(self, index):
        from .index.writer import writer
        with writer(self._index_output) as f:
            f.write(index)
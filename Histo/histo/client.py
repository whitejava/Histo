__all__ = ['commitfile', 'commitprevious']

import os
import io
from stream import objectstream, copy, tcpstream
from timetuple import totuple
from datetime import datetime

class client:
    def __init__(self, address):
        self._address = address
    
    def commitfile(self, name, path, time = None):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        lastmodify = totuple(datetime.fromtimestamp(os.path.getmtime(path)))
        filesize = os.path.getsize(path)
        stream.writeobject(time)
        stream.writeobject(name)
        stream.writeobject(lastmodify)
        stream.writeobject(os.path.basename(path))
        stream.writeobject(filesize)
        with open(path, 'rb') as f:
            copy(f, stream, filesize)
        assert stream.readobject() == 'ok'
    
    def commitprevious(self, filename):
        time, name = _resolvefilename(filename)
        self.commitfile(name, filename, time = time)
    
    def search(self, keyword):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        stream.writeobject(keyword)
        return stream.readobject()
    
    def get(self, range, path):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        stream.writeobject(range)
        length = range[1] - range[0]
        with open(path, 'wb') as f:
            copy(stream, f, length)

def _cut(string, pieces):
    #Stream
    string = io.StringIO(string)
    #Read pieces
    return [string.read(e) for e in pieces]

def _resolvefilename(filename):
    #Base name
    filename = os.path.basename(filename)
    #Extract datetime, name
    datetime, name = filename[:12], filename[12:-4]
    #Tuple datetime
    datetime = tuple([int(e) for e in _cut(datetime,[4,2,2,2,2])] + [0,0])
    #Strip underline in name
    if name.startswith('_'): name = name[1:]
    #Return
    return datetime, name
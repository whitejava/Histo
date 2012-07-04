import os
import io
from stream import objectstream, copy

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

def commitfile(name, filename, stream, time = None):
    #Object stream
    stream = objectstream(stream)
    #Output time
    stream.writeobject(time)
    #Output name
    stream.writeobject(name)
    #Output file size
    stream.writeobject(os.path.getsize(filename))
    #Output file data
    with open(filename, 'rb') as f:
        copy(f, stream)

def commitprevious(filename, stream = None):
    #Resolve file name
    time, name = _resolvefilename(filename)
    #Commit
    commitfile(name, filename, stream, time = time)
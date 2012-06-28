import struct
import os
import io
from stream import objectstream

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

def _transferstream(input, output, chunksize = 128*1024):
    while True:
        #Read chunk
        read = input.read(chunksize)
        #Check EOF
        if not read: break
        #Output
        output.write(read)

def commitprevious(filename, stream):
    #Object stream
    stream = objectstream(stream)
    #Resolve file name.
    datetime, name = _resolvefilename(filename)
    #Output name
    stream.writeobject(name)
    #Output datetime
    stream.writeobject(datetime)
    #Output file size
    stream.writeobject(os.path.getsize(filename))
    #Output file data
    with open(filename, 'rb') as f:
        _transferstream(f, stream)
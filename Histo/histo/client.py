import struct
import os
import io

def _packint(a):
    return struct.pack('!i',a)

def _packlong(a):
    return struct.pack('!q',a)

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

def commit(filename, output):
    #Resolve file name.
    datetime, name = _resolvefilename(filename)
    #Encode name
    name = name.encode('utf8')
    #Output name
    output.write(_packint(len(name)))
    output.write(name)
    #Output datetime
    output.write(_packint(len(datetime)))
    for e in datetime: output.write(_packint(e))
    #Output file size
    output.write(_packlong(os.path.getsize(filename)))
    #Output file data
    with open(filename, 'rb') as f:
        _transferstream(f, output)
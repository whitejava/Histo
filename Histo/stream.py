import struct
import pickle
import socket
import time, hashlib

__all__ = ['copy','datastream','objectstream']

def _packint(a):
    return struct.pack('!i',a)

def _packlong(a):
    return struct.pack('!q',a)

def _unpackint(a):
    return struct.unpack('!i', a)[0]

def _unpacklong(a):
    return struct.unpack('!q', a)[0]

def copy(input, output, limit = None, chunksize = 128*1024):
    result = 0
    for e in chunkreader(input, limit=limit, chunksize=chunksize):
        output.write(e)
        result += len(e)
    return result

def chunkreader(input, limit, chunksize):
    if limit is None:
        while True:
            read = input.read(chunksize)
            if not read:
                break
            yield read
    else:
        while limit > 0:
            readsize = min(chunksize, limit)
            read = input.read(readsize)
            if not read:
                break
            yield read
            limit -= len(read)

def bufferedreader(reader, buffercount = 5):
    buffer = []
    reading = True
    threadrunning = True
    def readthread():
        for e in reader:
            if len(buffer) < buffercount:
                buffer.append(e)
            else:
                while threadrunning and len(buffer) >= buffercount:
                    time.sleep(0.1)
        reading = False
    while reading:
        if buffer:
            yield buffer[0]
            del buffer[0]
        else:
            while reading and not buffer:
                time.sleep(0.1)

class datastream:
    def __init__(self, stream):
        self._stream = stream
    
    def write(self, data):
        self._stream.write(data)
    
    def writeint(self, a):
        self.write(_packint(a))
    
    def writelong(self, a):
        self.write(_packlong(a))
    
    def writebytes(self, a):
        self.writeint(len(a))
        self.write(a)
    
    def read(self, limit = None):
        return self._stream.read(limit)
    
    def readfully(self, limit):
        result = bytearray()
        while limit > 0:
            read = self.read(limit)
            if not read:
                raise EOFError()
            result.extend(read)
            limit -= len(read)
        return bytes(result)
    
    def readint(self):
        return _unpackint(self.readfully(4))
    
    def readlong(self):
        return _unpacklong(self.readfully(8))
    
    def readbytes(self):
        length = self.readint()
        result = self._stream.read(length)
        assert len(result) == length
        return result
    
class objectstream:
    def __init__(self, stream):
        self._stream = datastream(stream)
        
    def write(self, data):
        self._stream.write(data)
    
    def read(self, limit = None):
        return self._stream.read(limit)
    
    def writeobject(self, object):
        dump = pickle.dumps(object)
        self._stream.writeint(len(dump))
        self._stream.write(dump)
    
    def readobject(self):
        length = self._stream.readint()
        dump = self._stream.readfully(length)
        assert len(dump) == length
        return pickle.loads(dump)

class tcpstream:
    def __init__(self, target):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(target)
    
    def write(self, data):
        self._sock.sendall(data)
    
    def read(self, limit = None):
        if limit == None:
            limit = 1024
        return self._sock.recv(limit)

    def close(self):
        self._sock.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
        
class iostream:
    def __init__(self, input, output):
        self._input = input
        self._output = output
    
    def write(self, data):
        self._output.write(data)
    
    def read(self, limit = None):
        return self._input.read(limit)

class hashstream:
    def __init__(self, algorithm):
        self._hasher = hashlib.new(algorithm)
    
    def write(self, data):
        self._hasher.update(data)
    
    def digest(self):
        return self._hasher.digest()
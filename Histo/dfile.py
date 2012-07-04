__all__ = ['open']

from stream import objectstream
import io

class _reader:
    def __init__(self, bundle, partsize):
        self._bundle = bundle
        #Not closed
        self._closed = False
        #Read from beginning
        self._pointer = 0
        #Load state
        state = bundle.load(0)
        state = io.BytesIO(state)
        state = objectstream(state)
        self._partsize = state.readobject()
        self._filesize = state.readobject()
        assert partsize == self._partsize
    
    def read(self, limit = None):
        #Ensure not closed
        assert not self._closed
        #If read all
        if limit == None or limit > self.available():
            limit = self.available()
        #Define result
        result = bytearray()
        #Read 
        while limit:
            #Bundle id
            buffer = self._pointer//self._partsize+1
            #Load bundle
            buffer = self._bundle.load(buffer)
            #Create BytesIO
            buffer = io.BytesIO(buffer)
            #Skip to correct position
            partpos = self._pointer % self._partsize
            buffer.read(partpos)
            #
            partremain = self._partsize - partpos
            readsize = min(limit, partremain)
            #Read part
            read = buffer.read(readsize)
            assert len(read) == readsize
            #Decrease limit
            limit -= len(read)
            #Increase pointer
            self._pointer += len(read)
            #Output
            result.extend(read)
        #Return
        return bytes(result)
    
    def seek(self, position):
        assert 0 <= position <= self._filesize
        #Ensure not closed
        assert not self._closed
        #Set position
        self._pointer = position
    
    def available(self):
        return self._filesize - self._pointer
    
    def close(self):
        assert not self._closed
        self._closed = True

class _writer:
    def __init__(self, bundle, partsize):
        assert partsize > 0
        self._bundle = bundle
        #Check dfile exists
        if bundle.exists(0):
            #Load state
            state = bundle.load(0)
            state = io.BytesIO(state)
            state = objectstream(state)
            self._partsize = state.readobject()
            self._filesize = state.readobject()
            self._buffer = state.readobject()
            self._buffer = bytearray(self._buffer)
            assert self._filesize % self._partsize == len(self._buffer)
            assert partsize == self._partsize
        else:
            #Create state
            self._partsize = partsize
            self._filesize = 0
            self._buffer = bytearray()
        #Not closed
        self._closed = False
    
    def write(self, data):
        #Ensure not closed
        assert not self._closed
        #Append to buffer
        self._buffer.extend(data)
        #File new size
        self._filesize2 = self._filesize + len(data)
        #Flush buffer
        while len(self._buffer) >= self._partsize:
            #Target
            id = self._filesize//self._partsize+1
            #Data to write
            data = self._buffer[:self._partsize]
            #Clear from buffer
            del self._buffer[:self._partsize]
            #Dump data
            self._bundle.dump(id, data)
            #Increase file size.
            self._filesize += len(data)
        #Update file size.
        self._filesize = self._filesize2

    def tell(self):
        assert not self._closed
        return self._filesize

    def close(self):
        assert not self._closed
        self._closed = True
        #Flush buffer
        if self._buffer:
            id = self._filesize//self._partsize + 1
            buffer = bytes(self._buffer)
            self._bundle.dump(id, buffer)
        #Save state
        state = io.BytesIO()
        stream = objectstream(state)
        stream.writeobject(self._partsize)
        stream.writeobject(self._filesize)
        buffer = bytes(self._buffer)
        stream.writeobject(buffer)
        self._bundle.dump(0, state.getvalue())

def open(bundle, partsize, mode = 'rb'):
    t = {'rb': _reader,
         'wb': _writer}
    return t[mode](bundle, partsize)
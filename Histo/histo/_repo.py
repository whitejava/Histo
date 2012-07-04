from summary import generatesummary
from cipher import aes,hash
from bundle import local,crypto,monitor
import datetime
import stream
import pickle
import dfile
import os

def _securedfile(root, idformat, partsize, key, mode = 'wb', listener):
    b = []
    b.append(local(root, idformat))
    b.append(monitor(b[-1], lambda x:listener(b[0].getpath(x))))
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    b.append(crypto(b[-1], aes.cipher(key)))
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    return dfile.open(b[-1], partsize, mode)

def _totuple(t):
    return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

def _makeindex(time, name, lastmodify, range, summary):
    return (('version', time), ('name', name), ('last-modify',lastmodify), ('range',range), ('summary',summary))

class repo:
    def __init__(self, root, key, listener):
        self._key = key
        #Create index output
        path = os.path.join(root, 'index')
        format = 'i{:06d}'
        partsize = 1024*1024
        self._indexoutput = _securedfile(path, format, partsize, self._key, listener)
        #Create data output
        path = os.path.join(root, 'data')
        format = 'd{:08d}'
        partsize = 1024*1024
        self._dataoutput = _securedfile(path, format, partsize, self._key, listener)
    
    def commitfile(self, filename, name, time = None):
        #Default time is now
        if time == None: time = _totuple(datetime.datetime.now())
        #Start position
        start = self._dataoutput.tell()
        #Output data
        with open(filename, 'rb') as f: stream.copy(f, self._dataoutput)
        #End position
        end = self._dataoutput.tell()
        #Make index
        index = _makeindex(time,name,_totuple(datetime.datetime.fromtimestamp(os.path.getmtime(filename))),(start, end),generatesummary(name, filename))
        #Output index
        pickle.dump(index, self._indexoutput)
    
    def close(self):
        self._dataoutput.close()
        self._indexoutput.close()
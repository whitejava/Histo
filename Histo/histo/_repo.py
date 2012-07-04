from summary import generatesummary
from cipher import aes,hash
from bundle import local,crypto,monitor
import datetime
import stream
import pickle
import dfile
import os

def _securedfile(root, idformat, partsize, key, mode = 'wb'):
    bundle = local(root, idformat)
    bundle = monitor(bundle)
    bundle = crypto(bundle, hash.cipher('md5'))
    bundle = crypto(bundle, hash.cipher('sha1'))
    bundle = crypto(bundle, aes.cipher(key))
    bundle = crypto(bundle, hash.cipher('md5'))
    bundle = crypto(bundle, hash.cipher('sha1'))
    return dfile.open(bundle, partsize, mode)

def _totuple(t):
    return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

def _makeindex(time, name, lastmodify, range, summary):
    return (('version', time), ('name', name), ('last-modify',lastmodify), ('range',range), ('summary',summary))

class repo:
    def __init__(self, root, key):
        self._key = key
        #Create index output
        self._indexoutput = _securedfile(os.path.join(root, 'index'), 'i{:06d}', 1024*1024, self._key)
        #Create data output
        self._dataoutput = _securedfile(os.path.join(root, 'data'), 'd{:08d}', 1*1024*1024, self._key)
    
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
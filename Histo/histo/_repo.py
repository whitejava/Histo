import cipher.aes.cipher
import dfile.bundle.local.bundle as localbundle
import dfile.bundle.crypto.bundle as cryptobundle
import dfile.writer.writer
import dfile.files.files
import summary.generate_summary as generatesummary
import datetime
import stream
import os
import pickle

def _securedfile(root, idformat, partsize, key):
    cipher = cipher.aes.cipher.cipher(key)
    bundle = cryptobundle(localbundle(root, idformat), cipher)
    return dfile.writer.writer(dfile.files.files(bundle), partsize)

def _totuple(t):
    return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

def _makeindex(time, name, lastmodify, range, summary):
    return (('version', time), ('name', name), ('last-modify',lastmodify), ('range',range), ('summary',summary))

class repo:
    def __init__(self, root, key):
        #Create index output
        self._indexoutput = _securedfile(os.path.join(root, 'index'), 'i{:06d}', 1024*1024, self._key)
        #Create data output
        self._dataoutput = _securedfile(os.path.join(root, 'data'), 'd{:08d}', 10*1024*1024, self._key)
    
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
        index = _makeindex(time,name,_totuple(os.path.getmtime(filename)),(start, end),generatesummary(name, filename))
        #Output index
        pickle.dump(index, self._indexoutput)
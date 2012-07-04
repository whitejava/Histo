from summary import generatesummary
from cipher import aes,hash
from bundle import local,crypto,monitor
import datetime
import stream
import pickle
import dfile
import os

def _securedfile(root, idformat, partsize, key, listener):
    '''
    Create a safe distributed file.
    root: Root for dfile.
    idformat: for example '{:04d}' will creates 0000, 0001, 0002, etc.
    partsize: Distributed file is made up of many parts. This is the max size of each part.
    key: The key used to encrypt dfile.
    listener: Will be reported immediately after one part is changed.
    '''
    #Define bundle chain
    b = []
    #Local bundle
    b.append(local(root, idformat))
    #Monitor every dump
    b.append(monitor(b[-1], lambda x:listener(b[0].getpath(x))))
    #Verify
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    #Encrypt
    b.append(crypto(b[-1], aes.cipher(key)))
    #Verify
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    #DFile
    return dfile.open(b[-1], partsize, 'wb')

def _totuple(t):
    '''
    Translate a python datetime object into tuple object.
    '''
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
        lastmodify = os.path.getmtime(filename)
        lastmodify = datetime.datetime.fromtimestamp(lastmodify)
        lastmodify = _totuple(lastmodify)
        range = (start, end)
        summary = generatesummary(name, filename)
        index = _makeindex(time,name,lastmodify,range,summary)
        #Output index
        pickle.dump(index, self._indexoutput)
    
    def close(self):
        self._dataoutput.close()
        self._indexoutput.close()
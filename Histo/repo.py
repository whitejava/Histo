from bundle import local,crypto,monitor
import aes, hash
import dfile
import os

def _securedfile(root, mode, idformat, partsize, key, listener):
    '''
    Create a safe distributed file.
    root: Root for dfile.
    idformat: for example '{:04d}' will creates 0000, 0001, 0002, etc.
    partsize: Distributed file is made up of many parts. This is the max size of each part.
    key: The key used to encrypt dfile.
    listener: Will be reported immediately after one part is changed.
    '''
    b = []
    b.append(local(root, idformat))
    b.append(monitor(b[-1], lambda x:listener(x, b[0].getpath(x))))
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    b.append(crypto(b[-1], aes.cipher(key)))
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    return dfile.open(b[-1], partsize, mode)

class repo:
    def __init__(self, root, key, sendqueue):
        self._root = root
        self._key = key
        self._sendqueue = sendqueue
    
    def open(self, type, mode):
        typemarks = {'index': 'i',
                    'data': 'd',
                    'usage': 'u'}
        partsizes = {'index': 100*1024,
                     'data': 1024*1024,
                     'usage': 100*1024}
        mailboxsizes = {'index': 30000,
                       'data': 5000,
                       'usage': 20000}
        path = os.path.join(self._root, type)
        def onfileupdate(id, path):
            typemark = typemarks[type]
            mailboxsize = mailboxsizes[type]
            boxid = id // mailboxsize
            mailaddress = 'cpc.histo.{type}.{boxid}@gmail.com'.format(type = typemark, boxid = boxid)
            self._sendqueue.append((path, mailaddress))
        format = typemarks[type] + '{}'
        partsize = partsizes[type]
        return _securedfile(path, mode, format, partsize, self._key, onfileupdate)
from bundle import local,crypto,listen
import aes, hash, dfile, os

class repo:
    def __init__(self, root, key, mailclient):
        self._root = root
        self._key = key
        self._mailclient = mailclient
    
    def open(self, file, mode):
        mark = {'index':'i', 'data':'d','usage':'u'}[file]
        partsize = {'index': 100*1024, 'data': 1024*1024, 'usage': 100*1024}[file]
        boxsize = {'index': 20000, 'data': 5000, 'usage': 20000}
        receiver = 'cpc.histo.%s%d@gmail.com'
        path = os.path.join(self._root, file)
        b = [local(path, (mark+'{:d}').format)]
        b.append(listen(b[-1], onwrite = lambda x:self._mailclient.send(b[0].getpath(x), receiver%(mark, x//boxsize))))
        b.append(crypto(b[-1], hash.cipher('md5')))
        b.append(crypto(b[-1], hash.cipher('sha1')))
        b.append(crypto(b[-1], aes.cipher(self._key)))
        b.append(crypto(b[-1], hash.cipher('md5')))
        b.append(crypto(b[-1], hash.cipher('sha1')))
        return dfile.open(b[-1], partsize, mode)

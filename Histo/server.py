import threading, summary, tempfile
import os, io, sys, logging, shutil
import pclib, repo
from smtp import smtpserver
from pclib import copystream, objectstream, byteshex, netserver, nowtuple
from summary import generatesummary

logpath = 'E:\\histo-log\\0.log'
logdateformat = '[%Y-%m%d %H:%M:%S]'

#Log to file
logging.basicConfig(filename=logpath,
                    level=logging.DEBUG,
                    format='%(levelname)s - %(asctime)s %(message)s',
                    datefmt=logdateformat)

#Display log on console
formatter = logging.Formatter('%(asctime)s %(message)s')
formatter.datefmt = logdateformat
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# Usage:
# server root key threadcount

def main(root, key, threadcount = '5'):
    key = byteshex.decode(key)
    threadcount = int(threadcount)
    
    logging.debug('Loading smtp server')
    smtp = smtpserver(root, threadcount)
    
    logging.debug('Loading main server')
    main = mainserver(repo(root, key, smtp.getclient()))
    
    logging.debug('Starting main server')
    main.start()
    
    logging.debug('Starting smtp service')
    smtp.start()
    
    logging.debug('Service running')
    pclib.wait_for_keyboard_interrupt()
    
    logging.debug('Service shutting down')
    smtp.shutdown()
    main.shutdown()
    
    logging.debug('Now exit')
    
class mainserver(netserver):
    def __init__(self, repo):
        netserver.__init__(('127.0.0.1', 13750), self.handle)
        self._repo = repo
        self._index = loadindex()
        self._lock = threading.Lock()
    
    def handle(self, stream):
        method = stream.readobject()
        t = {'commitunpack': self.commitunpack,
             'search': self.search,
             'get': self.get}
        logging.debug('request: ' + method)
        with self._lock:
            try:
                t[method](stream)
            except Exception as e:
                logging.exception(e)
            else:
                logging.debug('ok')
    
    def commitunpack(self, stream):
        path = stream.readobject()
        compress = stream.readobject()
        logging.debug('path: ' + path)
        logging.debug('compress: ' + compress)
        
        name = os.path.basename(path) + '.rar'
        time = nowtuple()
        
        logging.debug('renaming')
        postfix = '-committing'
        shutil.move(path, path + postfix)
        path = path + postfix
        
        logging.debug('generating summary')
        summary = generatesummary(name, path, depthlimit = 2)
        
        logging.debug('packing')
        package = self.pack(name, path, compress)
        
        logging.debug('writing data')
        data = self._repo.open('data', 'wb')
        start = data.tell()
        with open(package, 'rb') as f:
            copystream(f, data)
        end = data.tell()
        
        logging.debug('writing index')
        item = (('datetime', time),
                ('name', name),
                ('last-modify', os.path.getmtime(path)),
                ('range', (start, end)),
                ('summary', summary))
        index = self._repo.open('data', 'wb')
        objectstream(index).writeobject(item)
        
        logging.debug('finishing')
        data.close()
        index.close()
        shutil.rmtree(path)
        self._index.append(loaditem(item))
        stream.writeobject('ok')
    
    def search(self, stream):
        keyword = stream.readobject()
        result = []
        for item in self._index:
            for text in summary.walk(item['summary']):
                if text.find(keyword) >= 0:
                    result.append(responseitem(item))
        return result
    
    def get(self, stream):
        start, end = stream.readobject()
        f = self._repo.open('data', 'rb')
        missing = f.getmissingpart(start, end)
        if missing:
            stream.writeobject('missing')
            stream.writeobject(missing)
        else:
            stream.writeobject('data')
            copystream(f, stream, end-start)
        f.close()
    
def pack(self, name, path, compress):
    root = 'G:\\'
    time = '%04d-%02d-%02d-%02d-%02d-%02d' % nowtuple()[:6]
    compress = {True: '-m5', False:'-m0'}[compress]
    package = os.path.join(root, '%s-%s' % (time, name))
    
    files = os.listdir(path)
    if not files:
        files = ['Empty']
        with open(os.path.join(path, 'Empty'), 'wb'): pass
    else:
        files = '\n'.join(files) + '\n'
        files = bytes(files, 'utf16')
        listfile = tempfile.NamedTemporaryFile(mode = 'wb', delete = False)
        listfile.write(files)
        listfile.close()
    
    cwd = os.getcwd()
    os.chdir(path)
    assert 0 == pclib.quietcall('rar a "%s" @"%s" -scul %s' % (package, listfile.name, compress))
    os.chdir(cwd)
    
    os.unlink(listfile.name)
    
    return package

def loaditem(x):
    return dict(x)

def responseitem(x):
    x = x.copy()
    del x['summary']
    return x

def loadindex(repo):
    try:
        f = repo.open('index', 'rb')
    except IOError:
        return []
    missing = f.getmissingparts()
    if missing:
        raise Exception('Missing: ' + ' '.join([str(e) for e in missing]))
    else:
        stream = objectstream(io.BytesIO(f.read()))
        f.close()
        result = []
        while True:
            try:
                result.append(loaditem(stream.readobject()))
            except EOFError:
                break
        return result

if __name__ == '__main__':
    main(*sys.argv[1:])
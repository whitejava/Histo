import threading, summary, tempfile, pickle
import os, io, sys, logging, shutil
import pclib
from pclib import copystream, objectstream, byteshex, netserver, nowtuple
from summary import generatesummary

default_logpath = 'E:\\histo-log\\0.log'
default_logformat = '%(levelname)s - %(asctime)s %(message)s'
default_logdateformat = '[%Y-%m%d %H:%M:%S]'
keysets = [
    ['Time', 'CommitCount', 'CodeCount', 'IndexCodes'],
    ['CommitID', 'Name', 'Time', 'Codes', 'Size', 'MD5', 'Summary'],
]

# Usage:
# server root key threadcount

def main(root, key, threadcount = '5'):
    key = byteshex.decode(key)
    threadcount = int(threadcount)
    
    initlogger(default_logpath, default_logformat, default_logdateformat)
    
    logging.debug('Loading histo server')
    histo = histoserver()
    histo.start()
    
    logging.debug('Services are running')
    pclib.wait_for_keyboard_interrupt()
    
    logging.debug('Services shutting down')
    histo.shutdown()
    
    logging.debug('Now exit')

def initlogger(logpath, logformat, logdateformat):
    #Log to file
    logging.basicConfig(filename=logpath,
                        level=logging.DEBUG,
                        format=logformat,
                        datefmt=logdateformat)
    
    #Display log on console
    formatter = logging.Formatter(logformat)
    formatter.datefmt = logdateformat
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

class histotime:
    @staticmethod
    def encode(timetuple):
        return '%04d-%02d%02d-%02d%02d%02d-%06d' % timetuple
    @staticmethod
    def decode(x):
        t = [e.split(',') for e in '0,4 5,7 7,9 10,12 12,14 14,16 17,23'.split()]
        return tuple([x[a,b] for a,b in t])

class histoserver(netserver):
    def __init__(self, config, statebundle, databundle, ):
        listenaddress = config['ListenAddress']
        listenport = config['ListenPort']
        netserver.__init__((listenaddress, listenport), self.handle)
        self.statebundle = statebundle
        self.databundle = databundle
        self.state = self.loadorcreatestate()
        self.lock = threading.Lock()
    
    def loadorcreatestate(self):
        statefile = self.getlateststatefile()
        if statefile is None:
            return self.createstate()
        else:
            return self.loadstate(statefile)

    def getlateststatefile(self):
        stateprefix = 'state-'
        allfiles = self.statebundle.list()
        if len(allfiles) is 0:
            return None
        statefiles = [e for e in allfiles if e.startswith(stateprefix)]
        latest = sorted(statefiles)[-1];
        return latest
    
    def createstate(self):
        return dict(list(zip(keysets[0], [pclib.nowtuple(), 0, 0, []])))
    
    def loadstate(self, statefile):
        with self.statebundle.open(statefile, 'rb') as f:
            stream = pclib.objectstream(f)
            keysetid = stream.readobject()
            values = stream.readobject()
        return dict(list(zip(keysets[keysetid], values)))
    
    def handle(self, stream):
        method = stream.readobject()
        t1 = 'commitunpack search get'.split()
        t2 = [self.commitunpack, self.search, self.get]
        t = dict(zip(t1, t2))
        logging.debug('request: ' + method)
        with self.lock:
            try:
                t[method](stream)
            except Exception as e:
                logging.exception(e)
            else:
                logging.debug('ok')

    def commitunpack(self, client):
        p = client.readobject()
        path = p['Path']
        compress = p['Compress']
        time = p['Time']
        if time is None:
            time = pclib.nowtuple()
        
        logging.debug('path: ' + path)
        
        name = os.path.basename(path) + '.rar'
        
        logging.debug('renaming')
        postfix = '-committing'
        path2 = path + postfix
        os.rename(path, path2)
        
        logging.debug('generating summary')
        summary = generatesummary(name, path, depthlimit = 2)
        
        logging.debug('packing')
        package = pack(name, path2, compress)
        packagesize = os.path.getsize(package)
        
        logging.debug('generating md5')
        with open(package, 'rb') as f:
            stream = pclib.hashstream('md5')
            copystream(f, stream)
        md5 = stream.digest()
        
        logging.debug('generating state')
        indexcodecount = 1
        packagecodecount = pclib.ceildiv(packagesize, self.config['MaxCodeSize'])
        oldstate = dict(self.state)
        newstate = dict(self.state)
        newstate['Time'] = pclib.nowtuple()
        newstate['CommitCount'] += 1
        newstate['CodeCount'] += indexcodecount + packagecodecount
        newstate['IndexCodes'] = oldstate['IndexCodes'] + [oldstate['CodeCount']]
        
        logging.debug('writing state')
        with self.statebundle.open('state-%s'%(histotime.encode(newstate['Time']))) as f:
            stream = objectstream(f)
            keysetid = 0
            stream.writeobject(keysetid)
            stream.writeobject(pclib.unzip(newstate, keysets[keysetid]))
        self.state = newstate
        
        logging.debug('generating index')
        index = dict()
        index['CommitID'] = oldstate['CommitCount']
        index['Name'] = name
        index['Time'] = newstate['Time']
        packagecodestart = oldstate['CodeCount'] + indexcodecount
        packagecodeend = packagecodestart + packagecodecount - 1
        index['Codes'] = [(packagecodestart, packagecodeend)]
        index['Size'] = packagesize
        index['MD5'] = md5
        index['Summary'] = summary
        
        logging.debug('writing index')
        with self.databundle.open('data-%08d' % oldstate['CodeCount'], 'rb') as f:
            stream = pclib.objectstream(f)
            keysetid = 1
            indexvalues = pclib.unzip(index, keysets[keysetid])
            stream.writeobject(keysetid)
            stream.writeobject(indexvalues)
        self.index.append([keysetid, indexvalues])
        
        logging.debug('writing data')
        with open(package, 'rb') as inputstream:
            for i in range(packagecodestart, packagecodeend + 1):
                bundlename = 'data-%08d' % i
                logging.debug('writing %s' % bundlename)
                with self.databundle.open(bundlename) as outputstream:
                    copystream(inputstream, outputstream, limit = self.config['MaxCodeSize'])
        
        logging.debug('cleaning up')
        shutil.rmtree(path2)
        client.writeobject('ok')
        logging.debug('commit ok')
    
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
    print('state-%04d-%02d%02d-%02d%02d%02d-%06d'%pclib.nowtuple())
    #main(*sys.argv[1:])
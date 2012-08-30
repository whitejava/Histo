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
'''
Server:
    commit:
        Commits a directory
        Parameters:
            p['Path']:
                The path to the target directory
            p['Compress']:
                Compress ratio.
                True:
                    High compress.
                False:
                    No compress.
            p['Time']:
                [Optional]
                Last modify time.
                None:
                    Current time on server.
        Return value:
            'ok':
                Successful.
    search:
        Search the whole histo-library.
        Parameters:
            keyword:
                The keyword you want to be searched.
                You can specify mutiple keywords by joining keywords by a space character.
        Return value:
            The search result, containing Name and Time,
            sorted by relevence.
    get:
        Get specified package.
        Parameters:
            commitid:
                The CommitID of the package you want to get.
        Return value:
            'ok':
                Successful
'''

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

class codesshorthand:
    @staticmethod
    def encode(start,end):
        if start == end:
            return [start]
        else:
            return [(start, end)]
    
    @staticmethod
    def walk(x):
        for e in x:
            if type(x) is tuple:
                for i in range(x[0], x[1]+1):
                    yield i
            else:
                yield e

class histoserver(netserver):
    def __init__(self, config, statebundle, databundle, ):
        listenaddress = config['ListenAddress']
        listenport = config['ListenPort']
        netserver.__init__((listenaddress, listenport), self.handle)
        self.statebundle = statebundle
        self.databundle = databundle
        self.state = self.loadorcreatestate()
        self.index = self.loadindex()
        self.lock = threading.Lock()
    
    def loadorcreatestate(self):
        statefile = self.getlateststatefile()
        if statefile is None:
            return self.createstate()
        else:
            return self.loadstate(statefile)

    def loadindex(self):
        codes = self.state['IndexCodes']
        for e in codesshorthand.walk(codes):
            with self.databundle.open('data-%08d'%e, 'rb') as f:
                stream = objectstream(f)
                while True:
                    try:
                        self.index.append(stream.readobject())
                    except EOFError:
                        break

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
        t1 = 'commit search get'.split()
        t2 = [self.commit, self.search, self.get]
        t = dict(zip(t1, t2))
        logging.debug('request: ' + method)
        with self.lock:
            try:
                t[method](stream)
            except Exception as e:
                logging.exception(e)
            else:
                logging.debug('ok')

    def commit(self, client):
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
        index['Codes'] = codesshorthand.encode(packagecodestart, packagecodeend)
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
        assert type(keyword) is str
        keywords = keyword.split()
        result = []
        for e in self.index:
            e = dict(zip(keysets[e[0]], e[1]))
            for text in summary.walk(e['Summary']):
                containcount = 0
                for e2 in keywords:
                    if text.find(e2) >= 0:
                        containcount += 1
                item = dict()
                item['Name'] = e['Name']
                item['Time'] = e['Time']
                item['ContainCount'] = containcount
                result.append(item)
        def cmp(x,y):
            if x['ContainCount'] < y['ContainCount']:
                return 1
            elif x['ContainCount'] > y['ContainCount']:
                return -1
            elif x['Time'] < y['Time']:
                return 1
            elif x['Time'] > y['Time']:
                return -1
            elif x['Name'] < y['Name']:
                return -1
            elif x['Name'] > y['Name']:
                return 1
            else:
                return 0
        result = [e for e in sorted(result, cmp=cmp)]
    
    def get(self, stream):
        commitid = stream.readobject()
        outputroot = 'D:'
        keysetid, values = self.index[commitid]
        item = zip(keysets[keysetid], values)
        assert item['CommitID'] is commitid
        codes = item['Codes']
        name = item['Name']
        time = item['Time']
        md5 = item['MD5']
        logging.debug('Name: ' + name)
        outputpath = os.path.join(outputroot, '%s-%s'%(histotime.encode(time),name))
        if os.path.exists(outputpath):
            stream.write('fail')
            logging.debug('Output exists')
            return
        outputstream1 = pclib.hashstream('md5')
        with open(outputpath, 'wb') as outputstream2:
            outputstream = pclib.streamhub(outputstream1, outputstream2)
            for e in codesshorthand.walk(codes):
                bundlename = 'data-%08d'%e
                logging.debug('Reading: ' + bundlename)
                with self.databundle.open(bundlename) as inputstream:
                    copystream(inputstream, outputstream)
        assert outputstream1.digest() == md5
        stream.write('ok')
        logging.debug('OK')
    
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

if __name__ == '__main__':
    #print('state-%04d-%02d%02d-%02d%02d%02d-%06d'%pclib.nowtuple())
    main(*sys.argv[1:])
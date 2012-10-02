def main():
    config = loadConfig()
    initLogger(config['Logger'])
    logger.debug('[ Load ExitSignal')
    exitSignal = ExitSignal()
    logger.debug(' ]')
    logger.debug('[ Load server')
    server = Server(config['Server'], exitSignal)
    logger.debug(' ]')
    logger.debug('[ Start server')
    server.start()
    logger.debug(' ]')
    logger.debug('[ Wait exit signal')
    waitForKeyboardInterruption()
    logger.debug(' ]')
    logger.debug('[ Shutdown')
    exitSignal.set()
    server.shutdown()
    logger.debug(' ]')

def loadConfig():
    import sys
    configFile = sys.argv[1]
    with open(configFile, 'r') as f:
        import json
        return json.load(f)

def ExitSignal():
    from threading import Event
    return Event()

def initLogger(config):
    import logging
    logFormat = config['LogFormat']
    logging.basicConfig(format=logFormat, level=logging.DEBUG)
    handler = logging.FileHandler(config['LogFile'])
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(logFormat))
    global logger
    logger = logging.getLogger()
    logger.addHandler(handler)

def Server(config, exitSignal):
    logger.debug('[ Load state bundle')
    stateBundle = StateBundle(config['StateBundle'], exitSignal)
    logger.debug(' ]')
    logger.debug('[ Load data bundle')
    dataBundle = DataBundle(config['DataBundle'], exitSignal)
    logger.debug(' ]')
    logger.debug('[ Load histo server')
    result = HistoServer(config['HistoServer'], stateBundle, dataBundle)
    logger.debug(' ]')
    return result

def waitForKeyboardInterruption():
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug('On keyboard interrupt')

def StateBundle(config, exitSignal):
    return FinalBundle(config, exitSignal)

def DataBundle(config, exitSignal):
    return FinalBundle(config, exitSignal)

def FinalBundle(config, exitSignal):
    from histo.bundle import Local, Buffer, Hub, Crypto
    fastBundle = Local(config['CachePath'])
    mailBundles = MailBundles(config['MailBundles'], exitSignal)
    slowBundle = Hub(mailBundles)
    cipher = Cipher(config['Cipher'])
    queueFile = config['QueueFile']
    usageLogFile = config['UsageLogFile']
    maxBufferSize = config['MaxBufferSize']
    threadCount = config['ThreadCount']
    volume = config['Volume']
    buffer = Buffer(fastBundle, slowBundle, queueFile, usageLogFile, maxBufferSize, threadCount, volume, exitSignal)
    return Crypto(buffer, cipher)

def MailBundles(config, exitSignal):
    return [Mail(e, exitSignal) for e in config]

def Cipher(config):
    from histo.cipher import Hub, AES, Verify
    from base64 import b16decode
    return Hub(Verify('md5'), AES(b16decode(bytes(config['Key'], 'utf8'))), Verify('sha1'), Verify('md5'))

def Mail(config, exitSignal):
    from histo.bundle import Mail as Mail2
    host = config['Host']
    port = config['Port']
    user = config['User']
    password = config['Password']
    receiver = config['Receiver']
    sender = config['Sender']
    return Mail2(host, port, user, password, receiver, sender, exitSignal)

from picklestream import PickleServer
class HistoServer(PickleServer):
    def __init__(self, config, stateBundle, dataBundle):
        PickleServer.__init__(self, (config['ListenIP'], config['ListenPort']))
        self.config = config
        self.stateBundle = stateBundle
        self.dataBundle = dataBundle
        self.state = self.loadOrCreateState()
        self.index = Index(self.openCodes(self.state['Codes']))
    
    def handle(self, stream):
        method = stream.readObject()
        t = {'Commit': self.commit,
             'Search': self.search,
             'Get': self.get}
        return t[method](stream)
    
    def commit(self, stream):
        parameters = stream.readObject()
        result = self.commit2(**parameters)
        stream.writeObject(result)
    
    def search(self, stream):
        parameters = stream.readObject()
        result = self.search2(**parameters)
        stream.writeObject(result)
    
    def get(self, stream):
        parameters = stream.readObject()
        self.get2(stream, **parameters)
    
    def loadOrCreateState(self):
        if self.getLatestState() is None:
            self.createState()
        return self.loadState()
    
    def openCodes(self, codes):
        for e in codes:
            with self.dataBundle.open('data-%08d' % e, 'rb') as f:
                yield f
    
    def commit2(self, Folder, Name = None, Compression = True, Time = None):
        return self.commit3(Folder, Name, Compression, Time)
    
    def commit3(self, folder, name, compression, time):
        import os.path
        time = self.translateTime(time)
        name = self.translateName(name, folder)
        folder = self.renameCommittingFolder(folder)
        archivePath = self.packFolder(folder, compression, time, name)
        dataSize = os.path.getsize(archivePath)
        dataCodes = self.copyToDataBundle(archivePath)
        md5 = getFileMD5(archivePath)
        indexItem = self.generateIndexItem(time, name, dataSize, dataCodes, md5, archivePath)
        indexCodes = self.pickleToDataBundle(KeySets.encode(1, indexItem))
        newState = self.generateNewState(indexCodes)
        self.state = newState
        self.pickleToStateBundle(KeySets.encode(0, newState))
        self.index.add(indexItem)
        self.deleteFolder(folder)
        return True
    
    def search2(self, Keywords):
        return self.search3(Keywords)
    
    def search3(self, keyWords):
        return self.index.search(keyWords)
    
    def get2(self, stream, CommitID):
        return self.get3(stream, CommitID)
    
    def get3(self, stream, commitId):
        item = self.index.getItemByCommitId(commitId)
        stream.writeobject(item['Size'])
        self.copyCodesFromDataBundle(item['Codes'], stream)
    
    def translateTime(self, time):
        if time is None:
            from pclib import nowtuple
            return nowtuple()
        return time
    
    def translateName(self, name, folder):
        if name is None:
            import os.path
            return os.path.basename(folder)
        return name
    
    def renameCommittingFolder(self, folder):
        folder2 = folder + '-committing'
        import os
        os.rename(folder, folder2)
        return folder2
    
    def copyFileToDataBundle(self, filePath):
        import os.path
        fileSize = os.path.getsize(filePath)
        with open(filePath, 'rb') as f:
            return self.copyToDataBundle(f, fileSize)
    
    def copyToDataBundle(self, f, fileSize):
        maxCodeSize = self.config['MaxCodeSize']
        dataCodeCount = self.state['CodeCount']
        copySize = 0
        result = []
        while copySize < fileSize:
            remainSize = fileSize - copySize
            size = min(remainSize, maxCodeSize)
            fileName = 'data-%08d' % dataCodeCount
            with self.dataBundle.open(fileName, 'wb') as f2:
                from pclib import copystream
                assert size == copystream(f, f2, size)
            result.append(dataCodeCount)
            copySize += size
            dataCodeCount += 1
        return result
    
    def pickleToDataBundle(self, x):
        import pickle
        import io
        data = pickle.dumps(x)
        f = io.BytesIO(data)
        return self.copyToDataBundle(f, len(data))
    
    def generateIndexItem(self, time, name, dataSize, dataCodes, md5, archivePath):
        index = dict()
        index['CommitID'] = self.state['CommitCount']
        index['Name'] = name
        index['Time'] = time
        index['Codes'] = CodesSimplify.encode(dataCodes)
        index['Size'] = dataSize
        index['MD5'] = md5
        from histo.summary import generateSummary
        index['Summary'] = generateSummary(name, archivePath)
    
    def pickleToStateBundle(self, state):
        import pickle
        data = pickle.dumps(state)
        time = state['Time']
        fileName = 'state-%04d%02d%02d%02d%02d%02d%06d' % time
        with self.stateBundle.open(fileName, 'wb') as f:
            f.write(data)
    
    def packFolder(self, folder, compression, time, name):
        import os
        import tempfile
        root = self.config['ArchiveRoot']
        timeString = '%04d%02d%02d%02d%02d%02d%06d' % time
        compress = {True: '-m5', False:'-m0'}[compression]
        package = os.path.join(root, '%s-%s' % (timeString, name))
        
        files = os.listdir(folder)
        if not files:
            files = ['Empty']
            with open(os.path.join(folder, 'Empty'), 'wb'): pass
        else:
            files = '\n'.join(files) + '\n'
            files = bytes(files, 'utf16')
            listfile = tempfile.NamedTemporaryFile(mode = 'wb', delete = False)
            listfile.write(files)
            listfile.close()
        
        cwd = os.getcwd()
        os.chdir(folder)
        import subprocess
        subprocess.call(['winrar a "%s" @"%s" -scul %s' % (package, listfile.name, compress)])
        os.chdir(cwd)
        
        os.unlink(listfile.name)
        
        return package
    
    def deleteFolder(self, folder):
        import shutil
        shutil.rmtree(folder)
    
    def createState(self):
        from pclib import nowtuple
        result = dict()
        result['Time'] = nowtuple()
        result['CommitCount'] = 0
        result['CodeCount'] = 0
        result['IndexCodes'] = []
        return result
    
    def copyCodesFromDataBundle(self, codeIds, stream):
        for codeId in codeIds:
            with self.dataBundle.open('data-%08d' % codeId) as f:
                from pclib import copystream
                copystream(f, stream)

class Index:
    def __init__(self, files):
        self.index = self.readIndexItems(files)
    
    def search(self, keyWords):
        matchCount = [self.countKeyWords(e['Summary'], keyWords) for e in self.Iterator()]
        result = [(e['Time'], e['CommitID'], e['Name'], e['Size']) for e in self.Iterator()]
        return [e[1] for e in sorted(zip(matchCount, result), reverse=True)]
    
    def add(self, indexItem):
        self.index.append(indexItem)
        
    def __iter__(self):
        for e in self.index:
            yield KeySets.decode(e)

def getFileMD5(file):
    from pclib import copystream, hashstream
    result = hashstream('md5')
    with open(file, 'rb') as f:
        copystream(f, result)
    return result.digest()

class CodesSimplify:
    @staticmethod
    def encode(codes):
        result = []
        while codes:
            maxContinuous = findMaxContinuous(codes)
            if maxContinuous == 1:
                result.append(codes[0])
            else:
                result.append((codes[0], codes[0] + maxContinuous - 1))
            del codes[:maxContinuous]
    
    @staticmethod
    def walk(x):
        for e in x:
            if type(e) is tuple:
                for f in range(e[0], e[1]):
                    yield f
            else:
                yield e

def findMaxContinuous(codes):
    for i in range(len(codes)):
        if codes[i] - codes[0] != i:
            return i + 1
    return len(codes)

class KeySets:
    @staticmethod
    def encode(self, keySetId, d):
        d = dict()
        result = []
        result.append(keySetId)
        for e in keySets(keySetId):
            result.append(d[e])
            del d[e]
        assert not d
        return result
    
    @staticmethod
    def decode(self, x):
        return dict(zip(keySets[x[0]], x[1:]))

keySets = [
    ['Time', 'CommitCount', 'CodeCount', 'IndexCodes'],
    ['CommitID', 'Name', 'Time', 'Codes', 'Size', 'MD5', 'Summary'],
]

if __name__ == '__main__':
    main()
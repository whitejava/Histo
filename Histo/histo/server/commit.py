import logging as logger

class Commit:
    def __init__(self, config, state, index, dataBundle, stream):
        self.config = config
        self.state = state
        self.index = index
        self.dataBundle = dataBundle
        self.stream = stream
    
    def run(self):
        logger.debug('[ Commit')
        self.readParameters()
        self.translateParameters()
        self.renameTargetFolder()
        self.ensureFolderNotEmpty()
        self.packTargetFolder()
        self.getPackageSize()
        self.getCurrentCodeCount()
        self.readPackageToDataBundle()
        self.generateIndexItem()
        self.pickleIndexItemToDataBundle()
        self.addIndexItemToIndex()
        self.generateNewState()
        self.updateState()
        self.deleteTargetFolder()
        self.writeOk()
        logger.debug(' ]')
    
    def readParameters(self):
        logger.debug('[ Read parameters')
        self.parameters = self.stream.readObject()
        logger.debug(' ]%s' % repr(self.parameters))
    
    def translateParameters(self):
        self.translateNameParameter()
        self.translateCompressionParameter()
        self.translateTimeParameter()
    
    def ensureFolderNotEmpty(self):
        import os
        if not os.listdir(self.targetFolder):
            emptyFile = os.path.join(self.targetFolder, 'empty')
            with open(emptyFile, 'wb'):
                pass
    
    def renameTargetFolder(self):
        folder = self.parameters['Folder']
        self.targetFolder = folder + '-commiting'
        import os
        os.rename(folder, self.targetFolder)
    
    def packTargetFolder(self):
        logger.debug('[ Pack folder')
        self.getArchivePath()
        packFolder(self.targetFolder, self.archivePath, self.compression)
        logger.debug(' ]')
    
    def getPackageSize(self):
        import os
        self.packageSize = os.path.getsize(self.archivePath)
    
    def getCurrentCodeCount(self):
        self.currentCodeCount = self.state['CodeCount']
    
    def readPackageToDataBundle(self):
        logger.debug('[ Read package to data bundle')
        with open(self.archivePath, 'rb') as f:
            self.dataCodes = self.readStreamToDataBundle(f, self.packageSize)
        logger.debug(' ]')
    
    def generateIndexItem(self):
        self.simplifyDataCodes()
        self.calculatePackageMd5()
        self.generateSummary()
        index = dict()
        index['CommitID'] = self.state['CommitCount']
        index['Name'] = self.name
        index['Time'] = self.time
        index['Codes'] = self.simplifiedDataCodes
        index['Size'] = self.packageSize
        index['MD5'] = self.packageMd5
        index['Summary'] = self.summary
        self.indexItem = index
    
    def pickleIndexItemToDataBundle(self):
        self.encodeIndexItem()
        self.pickleIndexItem()
        self.indexItemCodes = self.writeBytesToDataBundle(self.pickledIndexItem)
    
    def generateNewState(self):
        state = dict()
        state['Time'] = self.time
        state['CommitCount'] = self.state['CommitCount'] + 1
        state['CodeCount'] = self.currentCodeCount
        state['IndexCodes'] = self.state['IndexCodes'] + self.indexItemCodes
        self.newState = state
    
    def pickleNewStateToStateBundle(self):
        self.encodeNewState()
        self.pickleNewState()
        self.getStateName()
        self.writeBytesToStateBundle(self.pickledState)
    
    def addIndexItemToIndex(self):
        self.index.add(self.encodedIndexItem)
    
    def updateState(self):
        self.state.update(self.newState)
    
    def deleteTargetFolder(self):
        deleteFolder(self.targetFolder)
    
    def writeOk(self):
        self.stream.writeObject('OK')
    
    def translateNameParameter(self):
        default = self.getDefaultCommitName()
        self.name = self.parameters.get('Name', default)
    
    def translateCompressionParameter(self):
        default = True
        self.compression = self.parameters.get('Compression', default)
    
    def translateTimeParameter(self):
        from pclib import nowtuple
        default = nowtuple()
        self.time = self.parameters.get('Time', default)
    
    def getArchivePath(self):
        root = self.config['ArchiveRoot']
        import os
        self.getArchiveName()
        self.archivePath = os.path.join(root, self.archiveName)
    
    def readStreamToDataBundle(self, stream, size):
        maxCodeSize = self.config['MaxCodeSize']
        transferedSize = 0
        result = []
        while transferedSize < size:
            remainSize = size - transferedSize
            copySize = min(remainSize, maxCodeSize)
            result.append(self.currentCodeCount)
            dataName = 'data-%08d' % self.currentCodeCount
            with self.dataBundle.open(dataName, 'wb') as f:
                from pclib import copystream
                assert copystream(stream, f, copySize) == copySize
            self.currentCodeCount += 1
            transferedSize += copySize
        return result
    
    def simplifyDataCodes(self):
        from histo.server.codes import Codes
        self.simplifiedDataCodes = Codes.simplify(self.dataCodes)
    
    def calculatePackageMd5(self):
        logger.debug('[ Get package MD5')
        self.packageMd5 = calculateFileMd5(self.archivePath)
        logger.debug(' ]')
    
    def generateSummary(self):
        logger.debug('[ Generate summary')
        from histo.server.summary import generateSummary
        self.summary = generateSummary(self.name, self.targetFolder)
        logger.debug(' ]')
    
    def encodeIndexItem(self):
        from histo.server.keysets import KeySets
        self.encodedIndexItem = KeySets.encode(1, self.indexItem)
    
    def pickleIndexItem(self):
        import io
        result = io.BytesIO()
        from picklestream import PickleStream
        stream = PickleStream(result)
        stream.writeObject(self.encodedIndexItem)
        self.pickledIndexItem = result.getvalue()
    
    def writeBytesToDataBundle(self, b):
        import io
        stream = io.BytesIO(b)
        size = len(b)
        return self.readStreamToDataBundle(stream, size)
    
    def getDefaultCommitName(self):
        import os.path
        folder = self.parameters['Folder']
        return os.path.basename(folder)
    
    def getArchiveName(self):
        self.getTimeString()
        self.archiveName = '%s-%s.rar' % (self.timeString, self.name)
    
    def getTimeString(self):
        self.timeString = '%04d%02d%02d%02d%02d%02d%06d' % self.time
    
def calculateFileMd5(file):
    from pclib import copystream, hashstream
    result = hashstream('md5')
    with open(file, 'rb') as f:
        copystream(f, result)
    return result.digest()

def packFolder(folder, archivePath, compression):
    import os
    compress = {True: '-m5', False:'-m0'}[compression]
    cwd = os.getcwd()
    os.chdir(folder)
    import subprocess
    subprocess.call(['winrar', 'a', '-r', '-df', compress, archivePath, '.'])
    os.chdir(cwd)

def deleteFolder(folder):
    import os
    os.rmdir(folder)
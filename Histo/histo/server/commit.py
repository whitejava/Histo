class Commit:
    def __init__(self, config, state, index, dataBundle, stream):
        self.config = config
        self.state = state
        self.index = index
        self.dataBundle = dataBundle
        self.stream = stream
    
    def run(self):
        self.readParameters()
        self.translateParameters()
        self.renameTargetFolder()
        self.packTargetFolder()
        self.getPackageSize()
        self.getCurrentCodeCount()
        self.readPackageToDataBundle()
        self.generateIndexItem()
        self.pickleIndexItemToDataBundle()
        self.addIndexItemToIndex()
        self.updateState()
        self.deleteTargetFolder()
    
    def readParameters(self):
        self.parameters = self.stream.readObject()
    
    def translateParameters(self):
        self.translateNameParameter()
        self.translateCompressionParameter()
        self.translateTimeParameter()
    
    def renameTargetFolder(self):
        folder = self.parameters['Folder']
        self.targetFolder = folder + '-commiting'
        import os
        os.rename(folder, self.targetFolder)
    
    def packTargetFolder(self):
        self.getArchivePath()
        packFolder(self.targetFolder, self.archivePath, self.compression)
    
    def getPackageSize(self):
        import os
        self.packageSize = os.path.getsize(self.archivePath)
    
    def getCurrentCodeCount(self):
        self.currentCodeCount = self.state['CodeCount']
    
    def readPackageToDataBundle(self):
        with open(self.archivePath, 'rb') as f:
            self.dataCodes = self.readStreamToDataBundle(f, self.packageSize)
    
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
        pass
    
    def updateState(self):
        self.state.update(self.newState)
    
    def deleteTargetFolder(self):
        deleteFolder(self.targetFolder)
    
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
                assert copystream(stream, f) == copySize
            self.currentCodeCount += 1
        return result
    
    def simplifyDataCodes(self):
        from histo.server.codes import Codes
        self.simplifiedDataCodes = Codes.simplify(self.dataCodes)
    
    def calculatePackageMd5(self):
        self.packageMd5 = calculateFileMd5(self.archivePath)
    
    def generateSummary(self):
        from histo.server.summary import generateSummary
        self.summary = generateSummary(self.name, self.targetFolder)
    
    def encodeIndexItem(self):
        from histo.server.keysets import KeySets
        self.encodedIndexItem = KeySets.encode(1, self.indexItem)
    
    def pickleIndexItem(self):
        import io
        result = io.BytesIO()
        from picklestream import PickleStream
        stream = PickleStream(result)
        stream.writeObject(self.encodedIndexItem)
        return result.getvalue()
    
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
        pass
        self.getTimeString()
        return '%s-%s' % (self.timeString, self.name)
    
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
    subprocess.call(['winrar', 'a', '-r', compress, archivePath, '.'])
    os.chdir(cwd)

def deleteFolder(folder):
    import shutil
    shutil.rmtree(folder)
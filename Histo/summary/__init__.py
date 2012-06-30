import os
from autotemp import tempdir
from subprocess import Popen, PIPE

def _extractarchive(type, filename, target):
    command = {'rar': ['rar', 'x', filename, target+'/'],
               'tar': ['tar', '-xf', filename, '-C', target],
               'zip': ['unzip', filename, '-d', target]}
    command = command[type]
    rarmessage = {1: 'warning',
                  2: 'fatal error',
                  3: 'CRC fail',
                  4: 'locked archive',
                  5: 'write file error',
                  6: 'open file error',
                  7: 'user error',
                  8: 'not enough memory',
                  9: 'create file error',
                  10: 'no file to extract',
                  255: 'user abort'}
    tarmessage = {1: 'error occurs',
                  2: 'bad tar file'}
    zipmessage = {1: 'warning',
                  2: 'generic format error',
                  3: 'severe format error',
                  4: 'not enough memory at startup',
                  5: 'fail read password',
                  6: 'not enough memory during disk decompression',
                  7: 'not enough memory during in-memory decompression',
                  9: 'zipfile not found',
                  10: 'invalid option',
                  11: 'no matching files found',
                  80: 'aborted',
                  81: 'unsupport compression method',
                  82: 'bad password'}
    message = {'rar': rarmessage,
               'tar': tarmessage,
               'zip': zipmessage}
    proc = Popen(command, stdin = PIPE)
    proc.stdin.close()
    exitcode = proc.wait()
    if exitcode:
        message = message[type]
        if exitcode in message.keys():
            message = message[exitcode]
        else:
            message = 'unknown exitcode {}'.format(exitcode)
        raise extracterror(message)

class extracterror(OSError):
    def __init__(self, message):
        self.message = message
    
    def __repr__(self):
        return 'extracterror({})'.format(repr(self.message))

def _foldersummary(folder):
    #Generate each summary of files in folder
    return tuple([generatesummary(file, os.path.join(folder, file)) for file in os.listdir(folder)])

def _archivesummary(archivetype, filename):
    with tempdir('histo-summary-') as temp:
        error = None
        try:
            _extractarchive(archivetype, filename, temp)
        except extracterror as e:
            error = str(e)
        return (archivetype, error, _foldersummary(temp))

def _rar_summary(filename):
    return _archivesummary('rar', filename)

def _tar_summary(filename):
    return _archivesummary('tar', filename)

def _zip_summary(filename):
    return _archivesummary('zip', filename)

_map = {
    '.rar': _rar_summary,
    '.tar': _tar_summary,
    '.tar.gz': _tar_summary,
    '.tar.bz2': _tar_summary,
    '.zip': _zip_summary,
}

def generatesummary(name, filename):
    if os.path.isdir(filename):
        return (name, _foldersummary(filename))
    else:
        for k in _map:
            if filename.endswith(k):
                return (name, _map[k](filename))
        return (name, None)
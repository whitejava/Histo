import os
from autotemp import tempdir
from subprocess import Popen, PIPE

__all__ = ['generatesummary']

def generatesummary(name, filename):
    if os.path.isdir(filename):
        return (name, _foldersummary(filename))
    else:
        table = {
            '.rar': lambda x:_archivesummary('rar',x),
            '.tar': lambda x:_archivesummary('tar',x),
            '.tar.gz': lambda x:_archivesummary('tar',x),
            '.tar.bz2': lambda x:_archivesummary('tar',x),
            '.zip': lambda x:_archivesummary('zip',x),
        }
        for k in table:
            if filename.endswith(k):
                return (name, table[k](filename))
        return (name, None)

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
                  10: 'no input file',
                  255: 'user abort'}
    tarmessage = {1: 'error occurs',
                  2: 'no input file'}
    zipmessage = {1: 'warning',
                  2: 'generic format error',
                  3: 'severe format error',
                  4: 'not enough memory at startup',
                  5: 'fail read password',
                  6: 'not enough memory during disk decompression',
                  7: 'not enough memory during in-memory decompression',
                  9: 'no input file',
                  10: 'invalid option',
                  11: 'no input file because no matching files found',
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
        raise _extracterror(message)

class _extracterror(OSError):
    def __repr__(self):
        return 'extracterror({})'.format(repr(self.args[0]))

def _foldersummary(folder):
    #List files.
    files = os.listdir(folder)
    #Generate each summary of each file.
    return tuple([generatesummary(file, os.path.join(folder, file)) for file in files])

def _archivesummary(archivetype, filename):
    with tempdir('histo-summary-') as temp:
        error = None
        try:
            _extractarchive(archivetype, filename, temp)
        except _extracterror as e:
            error = repr(e)
        return (archivetype, error, _foldersummary(temp))
from ._reader import reader
from ._writer import writer

def open(files, partsize, mode = 'rb'):
    t = {'rb': reader, 'wb': writer}
    return t[mode](files, partsize)
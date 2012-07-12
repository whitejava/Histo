from netserver import netserver
from autotemp import tempdir
from timetuple import nowtuple
from stream import copy, objectstream
from summary import generatesummary
from histo.repo import repo
import pchex
import sys
import os

def main():
    root = sys.argv[1]
    key = sys.argv[2]
    key = pchex.decode(key)
    ip = sys.argv[3]
    server(root, key, ip).run()

class server(netserver):
    def __init__(self, root, key, ip):
        self._repo = repo(root, key, (ip, 13751))
    
    def handle(self, stream):
        method = stream.readobject()
        assert method == 'commit'
        datetime = stream.readobject()
        if datetime == None:
            datetime = nowtuple()
        name = stream.readobject()
        lastmodify = stream.readobject()
        filename = stream.readobject()
        filesize = stream.readobject()
        with tempdir('histo-repo-') as t:
            temp = os.path.join(t, filename)
            with open(temp, 'wb') as f:
                copy(stream, f, filesize)
            datafile = self._repo.open('data', 'wb')
            start = datafile.tell()
            with open(temp, 'rb') as f:
                copy(f, datafile, filesize)
            end = datafile.tell()
            summary = generatesummary(name, temp)
            index = (('datetime', datetime),
                     ('name', name),
                     ('last-modify', lastmodify),
                     ('range', (start, end)),
                     ('summary', summary))
            indexfile = self._repo.open('index', 'wb')
            objectstream(indexfile).writeobject(index)
            datafile.close()
            indexfile.close()
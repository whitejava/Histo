from stream import tcpstream
from listfiles import listfiles
import histo.server
import histo.client
import histo.search.server
import pchex
import sys
import os

def commitprevious(root, ip):
    for e in listfiles(root):
        path = os.path.join(root, e)
        with tcpstream((ip, 13750)) as stream:
            histo.client.commitprevious(path, stream)

def serveforever(root, key):
    key = pchex.decode(key)
    histo.server.serveforever(root, key)

def searchengine(index, key):
    key = pchex.decode(key)
    histo.search.server.serveforever(index, key)

if __name__ == '__main__':
    command = sys.argv[1]
    t = {'server': serveforever,
         'commitprevious': commitprevious}
    t[command](*sys.argv[2:])
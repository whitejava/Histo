from stream import tcpstream
import histo.server
import sys
import hex

def commitprevious(filename, ip):
    stream = tcpstream((ip,13750))
    histo.client.commitprevious(filename, stream)

def serveforever(root, key):
    key = hex.decode(key)
    histo.server.serveforever(root, key)

if __name__ == '__main__':
    command = sys.argv[1]
    t = {'server': serveforever,
         'commitprevious': commitprevious}
    t[command](sys.argv[2:])
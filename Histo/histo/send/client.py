from stream import tcpstream, objectstream

def addqueue(address, x):
    stream = tcpstream(address)
    stream = objectstream(stream)
    stream.writeobject('add')
    stream.writeobject(x)
    assert stream.readobject() == 'ok'
    stream.close()
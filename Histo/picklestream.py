class PickleStream:
    def __init__(self, stream):
        from pclib import datastream
        self.stream = datastream(stream)
        
    def write(self, data):
        self.stream.write(data)
    
    def read(self, limit = None):
        return self.stream.read(limit)
    
    def writeObject(self, object2):
        import pickle
        dump = pickle.dumps(object2)
        self.stream.writeint(len(dump))
        self.stream.write(dump)
    
    def readObject(self):
        import pickle
        length = self.stream.readint()
        dump = self.stream.readfully(length)
        assert len(dump) == length
        return pickle.loads(dump)
    
    def close(self):
        self.stream.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()

class PickleServer:
    def __init__(self, address):
        handler = self.handle
        from socketserver import StreamRequestHandler
        class Handler(StreamRequestHandler):
            def handle(self):
                from pclib import iostream
                stream = iostream(self.rfile, self.wfile)
                stream = PickleStream(stream)
                handler(stream)
        from socketserver import TCPServer
        self.server = TCPServer(address, Handler)
    
    def start(self):
        from threading import Thread
        Thread(target = self.run).start()
    
    def run(self):
        self.server.serve_forever()
    
    def shutdown(self):
        self.server.shutdown()
    
    def handle(self, stream):
        pass

def PickleClient(address):
    from pclib import tcpstream
    return PickleStream(tcpstream(address))
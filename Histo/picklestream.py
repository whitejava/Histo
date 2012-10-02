class PickleServer:
    def __init__(self, address):
        handler = self.handle
        from socketserver import StreamRequestHandler
        class Handler(StreamRequestHandler):
            def handle(self):
                from pclib import iostream, objectstream
                stream = iostream(self.rfile, self.wfile)
                stream = objectstream(stream)
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
    from pclib import tcpstream, objectstream
    return objectstream(tcpstream(address))
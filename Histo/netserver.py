from socketserver import StreamRequestHandler, TCPServer
from stream import iostream, objectstream
from threading import Thread

class netserver:
    def __init__(self, address, handler):
        class a(StreamRequestHandler):
            def handle(self):
                stream = iostream(self.rfile, self.wfile)
                stream = objectstream(stream)
                handler(stream)
        self._server = TCPServer(address, a)
    
    def start(self):
        Thread(target = self.run).start()
    
    def run(self):
        self._server.serve_forever()
    
    def shutdown(self):
        self._server.shutdown()
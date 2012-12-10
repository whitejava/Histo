config = {'Timeout': 5}

class MobileServer:
    def __init__(self, address):
        ''' @param address: A tuple of ip and port. '''
        from socketserver import TCPServer
        self.server = TCPServer(address, MobileHandler)
        
    def run(self):
        self.server.serve_forever()

class Session:
    def onFolder(self):
        pass
    
    def onFile(self):
        pass
    
    def onBye(self):
        pass

class MobileHandler:
    def handle(self, stream):
        self.session = Session()
        from pclib import datastream
        self.stream = datastream(stream)
        self.request = self.readRequest()
        handler = getattr(self, 'handle'+self.request['Command'])
        handler()
        
    def handleFolder(self):
        self.session.onFolder()
        self.response('OK')
        
    def handleFile(self):
        self.response('OK')
        
    def handleBye(self):
        self.response('Bye')
    
    def readRequest(self):
        request = self.stream.readbytes()
        request = str(request, 'utf8')
        import json
        request = json.loads(request)
        return request
    
    def response(self, message):
        self.stream.writebytes(bytes(message, 'utf8'))

if __name__ == '__main__':
    MobileServer().run()
import os
from stream import objectstream, copy, iostream
from socketserver import StreamRequestHandler, TCPServer
from autotemp import tempdir
from ._repo import repo
from threading import Thread
import threading
import pickle
import time
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import dns.resolver
import hashlib
from filelock import filelock
import hex

_shutdowns = []

def log(*message):
    t = '[{:13f}]'.format(time.clock())
    print(t, *message)

class sendqueue:
    def __init__(self, file):
        self._file = file
        self._lock = threading.Lock()
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                self._queue = pickle.load(f)
        else:
            self._queue = []
            self._save()
    
    def empty(self):
        with self._lock:
            return self._queue == []
    
    def front(self):
        with self._lock:
            return self._queue[0]
    
    def append(self, x):
        with self._lock:
            for i in range(1, len(self._queue)):
                if self._queue[i] == x:
                    del self._queue[i]
                    break
            self._queue.append(x)
            self._save()
    
    def pop(self):
        with self._lock:
            del self._queue[0]
            self._save()
    
    def _save(self):
        with open(self._file, 'wb') as f:
            pickle.dump(self._queue, f)

def _queuesend(path):
    global _sendqueue
    _sendqueue.append(path)

def _acceptservice(root, key):
    class _commithandler(StreamRequestHandler):
        def handle(self):
            with tempdir('histo-') as td:
                stream = iostream(self.rfile, self.wfile)
                stream = objectstream(stream)
                time = stream.readobject()
                name = stream.readobject()
                filename = stream.readobject()
                filesize = stream.readobject()
                temp = os.path.join(td, filename)
                with open(temp, 'wb') as f:
                    copy(stream, f, limit = filesize)
                assert filesize == os.path.getsize(temp)
                log('accept', name)
                rp = repo(root, key, _queuesend)
                rp.commitfile(temp, time = time, name = name)
                rp.close()
                stream.writeobject('OK')
    #Create tcp server
    server = TCPServer(('0.0.0.0',13750), _commithandler)
    #Add shutdown list
    _shutdowns.append(server.shutdown)
    #Log
    log('listening')
    #Run server
    server.serve_forever()

def sendmail(sender, receiver, subject, content, attachmentname, attachmentdata):
    message = MIMEMultipart()
    message['From'] = '<{}>'.format(sender)
    message['To'] = '<{}>'.format(receiver)
    message['Subject'] = subject
    message.attach(MIMEText(content))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachmentdata)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(attachmentname))
    message.attach(part)
    message = message.as_string()
    host = receiver.split('@')
    host = host[-1]
    host = dns.resolver.query(host, 'MX')
    host = host[-1]
    host = host.to_text()
    host = host.split(' ')
    host = host[1]
    host = dns.resolver.query(host, 'A')
    host = host[0]
    host = host.to_text()
    port = 25
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    def recv(code):
        data = sock.recv(1024)
        data = data[:-2]
        data = str(data, 'utf8')
        data = data.split(' ')
        data = data[0]
        data = int(data)
        assert data == code
    def send(m):
        sock.sendall(bytes(m+'\r\n','utf8'))
    try:
        recv(220)
        send('HELO caipeichao.com')
        recv(250)
        send('MAIL FROM:<{}>'.format(sender))
        recv(250)
        send('RCPT TO:<{}>'.format(receiver))
        recv(250)
        send('DATA')
        for line in message.splitlines():
            send(line)
        send('.')
        recv(354)
        send('QUIT')
        recv(250)
    finally:
        sock.close()

def _successsend(filename):
    while True:
        try:
            name = os.path.basename(filename)
            sender = 'histo@caipeichao.com'
            type = name[0]
            boxid = name[1:]
            boxid = int(boxid)
            boxid = boxid // 5000
            receiver = 'cpc.histo.{}{}'.format(type, boxid)
            with filelock(filename):
                with open(filename, 'rb') as f:
                    data = f.read()
            hash = hashlib.new('md5', data).digest()
            hash = hex.encode(hash)
            sendmail(sender, receiver, name, hash, name, data)
        except BaseException as e:
            raise
            log('SMTP Error: ' + str(e))
        else:
            return

def _sendservice():
    global _sendqueue
    while True:
        if not _sendqueue.empty():
            f = _sendqueue.front()
            _successsend(f)
            _sendqueue.pop()
        time.sleep(1)

def _startthread(callable):
    Thread(target = callable).start()

def serveforever(root, key):
    global _sendqueue
    _sendqueue = sendqueue(os.path.join(root, 'sendqueue'))
    _startthread(lambda:_acceptservice(root, key))
    _startthread(lambda:_sendservice())
    try:
        while True:
            time.sleep(0.1)
    finally:
        log('shutting down')
        for e in _shutdowns: e()
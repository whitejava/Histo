from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import dns.resolver
import socket

class smtpserver:
    def __init__(self, root, threadcount = 5):
        self._threadcount = threadcount
        self._queue = sendqueue(root)
    
    def start(self):
        self._threads = [sendthread() for _ in range(self._threadcount)]
        for e in self._threads:
            e.start()
    
    def shutdown(self):
        for e in self._threads:
            e.shutdownsignal()
        for e in self._threads:
            e.wait()
    
    def getclient(self):
        return smtpclient(self._queue)

    



def sendmail(sender, receiver, subject, content, attachmentname, attachmentdata, stopper = [False]):
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
        assert not stopper[0]
        data = sock.recv(1024)
        data = data[:-2]
        data = str(data, 'utf8')
        data = data.split(' ')
        data = data[0]
        data = int(data)
        assert data == code
    def send(data):
        assert not stopper[0]
        sock.sendall(bytes(data + '\r\n','utf8'))
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

class sendthread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self._queue = queue
        self._stopper = [False]
        self._exitlock = threading.Lock()
        self._exitlock.acquire()
    
    def shutdown(self):
        self._stopper[0] = True
    
    def wait(self):
        self._exitlock.acquire()
        self._exitlock.release()
    
    def run(self):
        try:
            while not self._stopper[0]:
                time.sleep(1)
                try:
                    taskid, each = self._queue.fetchtask()
                except NoTask:
                    continue
                path = each[0]
                receiver = each[1]
                name = os.path.basename(path)
                logging.debug('fetch ' + name)
                with filelock(path):
                    lastmodify = os.path.getmtime(path)
                    filesize = os.path.getsize(path)
                    with open(path, 'rb') as f:
                        data = f.read()
                    assert len(data) == filesize
                lastmodify = datetime.fromtimestamp(lastmodify)
                lastmodify = totuple(lastmodify)
                lastmodify = '{:04d}-{:02d}{:02d}-{:02d}{:02d}{:02d}-{:06d}'.format(*lastmodify)
                md5 = pchex.encode(hashlib.new('md5', data).digest())
                sender = 'histo@caipeichao.com'
                subject = name
                content = '%s-%s-%s' % (filesize, lastmodify, md5)
                attachmentname = name
                attachmentdata = data
                logging.debug('sending {} to {}'.format(name, receiver))
                try:
                    smtp.sendmail(sender, receiver, subject, content, attachmentname, attachmentdata, stopper = self._stopper)
                except Exception as e:
                    logging.warning('fail send %s' % name)
                    self._queue.feedback(taskid, False)
                else:
                    self._queue.feedback(taskid, True)
                    logging.debug('finish send {}'.format(name))
        except Exception as e:
            logging.exception(e)
        finally:
            self._exitlock.release()

class smtpserver:
    def __init__(self, root, threadcount = 5):
        self._threadcount = threadcount
        self._queue = taskqueue(diskqueue(os.path.join(root, 'sendqueue')))
    
    def getqueue(self):
        return self._queue
    
    def start(self):
        self._threads = [sendthread(self._queue) for i in range(self._threadcount)]
        for e in self._threads:
            e.start()
    
    def shutdown(self):
        for e in self._threads:
            e.shutdown()
        for e in self._threads:
            e.wait()
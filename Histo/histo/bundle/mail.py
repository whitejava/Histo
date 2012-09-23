class Mail:
    def __init__(self, host, port, user, password, emailAddress):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.emailAddress = emailAddress
        self.files = self.listFiles()
    
    def open(self, name, mode):
        if mode == 'rb':
            return self.openForRead(name)
        elif mode == 'wb':
            return self.openForWrite(name)
        else:
            raise Exception('No such mode.')
    
    def delete(self, name):
        raise Exception('Not impl')
    
    def list(self):
        return [e[1] for e in self.files]
    
    def getConnection(self):
        return ImapConnection(self.host, self.port, self.user, self.password)
    
    def listFiles(self):
        with self.getConnection() as connection:
            mails = connection.search(None, 'ALL')
            mails = mails[1][0]
            mails = str(mails,'utf8').split()
            mails = ','.join(mails)
            result = connection.fetch(mails, '(BODY.PEEK[HEADER.FIELDS (Subject)])')
            result = result[1][::2]
            result = [str(e[1], 'utf8') for e in result]
            for e in result:
                assert e.startswith('Subject: ')
                assert e.endswith('\r\n\r\n')
            result = [e[9:-4] for e in result]
            return list(zip(map(int, mails), map(decodeString, result)))
    
    def openForRead(self, name):
        with self.getConnection() as connection:
            return self.openForRead2(connection, name)
    
    def openForWrite(self, name):
        with self.getConnection() as connection:
            return self.openForWrite2(connection, name)
    
    def openForRead2(self, connection, name):
        data = connection.fetch(str(self.getMailIdByName(name)))
        emailBody = data[1][0][1]
        import email
        mail = email.message_from_string(emailBody)
        for part in mail.walk():
            if part.get('Content-Disposition') is not None:
                import io
                return io.BytesIO(part.get_payload(decode=True))
        raise Exception('Message abnormal.')
    
    def openForWrite2(self, connection, name):
        return MailWriter(self.emailAddress, name)
    
    def getMailIdByName(self, name):
        for e in self.files:
            if e[1] == name:
                return e[0]
        raise Exception('No such mail ' + name)

def decodeString(x):
    import re
    import quopri
    match = re.match(r'=\?(?P<encode>.*)\?(?P<data>.*)', x)
    if match:
        encode = match.group('encode')
        data = match.group('data')
        data = quopri.decodestring(data)
        return str(data, encode)
    return quopri.decodestring(x)

class ImapConnection:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.refCount = 0
        from threading import Lock
        self.lock = Lock()
        
    def __enter__(self):
        with self.lock:
            if self.refCount:
                return self.connection
            else:
                connection = self.Connection()
                self.connection = connection
                self.refCount += 1
                return connection
    
    def __exit__(self, *k):
        with self.lock:
            self.refCount -= 1
            if self.refCount == 0:
                self.connection.close()
                self.connection.logout()

    def Connection(self):
        from imaplib import IMAP4_SSL
        result = IMAP4_SSL(self.host, self.port)
        result.login(self.user, self.password)
        result.select(None, 'INBOX')
        return result

class MailWriter:
    def __init__(self, sender, receiver, name):
        self.sender = sender
        self.receiver = receiver
        self.name = name
        import io
        self.buffer = io.BytesIO()
        
    def write(self, data):
        return self.buffer.write(data)
        
    def close(self):
        sendMail(self.sender, self.receiver, self.name, '', self.name, self.buffer.getvalue())
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
    
def sendMail(sender, receiver, subject, content, attachmentname, attachmentdata, stopper = [False]):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import dns.resolver
    import socket
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
        send('HELO %s' % sender.split('@')[1])
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
import logging as logger

def retry(times):
    def a(f):
        def b(*k, **kw):
            lastException = None
            for i in range(times):
                try:
                    return f(*k, **kw)
                except Exception as e:
                    logger.debug('Exception in retry %d: %s' % (i, repr(e)))
                    logger.exception(e)
                    lastException = e
            raise lastException
        return b
    return a

class Mail:
    def __init__(self, config, exitSignal):
        self.config = config
        self.exitSignal = exitSignal
        from threading import Lock
        self.lock = Lock()
    
    @retry(10)
    def open(self, name, mode):
        if mode == 'rb':
            return self.openForRead(name)
        elif mode == 'wb':
            return self.openForWrite(name)
        else:
            raise Exception('No such mode.')
    
    @retry(10)
    def delete(self, name):
        raise Exception('Not impl')
    
    @retry(10)
    def list(self):
        return [e['Name'] for e in self.listFiles()]
    
    @retry(10)
    def getTotalSize(self):
        return sum([e['Size'] for e in self.listFiles()])
    
    def listFiles(self):
        with self.lock:
            with self.Connection() as connection:
                mails = connection.search(None, 'ALL')
                mails = mails[1][0]
                mails = str(mails,'utf8').split()
                if not mails:
                    return []
                mails2 = ','.join(mails)
                response = connection.fetch(mails2, '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
                subjects = parseResponse(response)
                result = []
                for i in range(len(subjects)):
                    d = dict()
                    d['MailID'] = int(mails[i])
                    x = MailSubject.decode(subjects[i])
                    d['Size'] = x[0]
                    d['Name'] = x[1]
                    result.append(d)
                return result
    
    def openForRead(self, name):
        with self.Connection() as connection:
            return self.openForRead2(connection, name)
    
    def openForWrite(self, name):
        return MailWriter(self.config['Smtp'], name, self.exitSignal)
    
    def openForRead2(self, connection, name):
        data = connection.fetch(str(self.getMailIdByName(name)), '(RFC822)')
        emailBody = data[1][0][1]
        import email
        mail = email.message_from_string(str(emailBody,'utf8'))
        for part in mail.walk():
            if part.get('Content-Disposition') is not None:
                import io
                return io.BytesIO(part.get_payload(decode=True))
        raise Exception('Message has no attachment.')
    
    def getMailIdByName(self, name):
        for e in self.listFiles():
            if e['Name'] == name:
                return e['MailID']
        raise Exception('No such mail')
    
    def Connection(self):
        return ImapConnection(self.config['Imap'])

class ImapConnection:
    def __init__(self, config):
        self.host = config['Host']
        self.port = config['Port']
        self.user = config['User']
        self.password = config['Password']
        self.refCount = 0
        from threading import Lock
        self.lock = Lock()
        
    def __enter__(self):
        with self.lock:
            if self.refCount:
                self.refCount += 1
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
        result.select('INBOX')
        return result

class MailWriter:
    def __init__(self, config, name, exitSignal):
        self.host = config['Host']
        self.sender = config['Sender']
        self.receiver = config['Receiver']
        self.name = name
        self.exitSignal = exitSignal
        import io
        self.buffer = io.BytesIO()
        
    def write(self, data):
        return self.buffer.write(data)
        
    def close(self):
        data = self.buffer.getvalue()
        size = len(data)
        subject = MailSubject.encode(self.name, size)
        sendMail(self.host, self.sender, self.receiver, subject, '', self.name, data, self.exitSignal)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()

class MailSubject:
    @staticmethod
    def encode(name, size):
        return '%08d - %s' % (size, name)
    
    @staticmethod
    def decode(string):
        assert string[8:11] == ' - '
        size = string[:8]
        name = string[11:]
        return size, name

def sendMail(host, user, password, sender, receiver, subject, content, attachmentname, attachmentdata, exitSignal):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
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
    port = 25
    localHostName = sender.split('@')[1]
    
    from smtplib import SMTP
    smtp = SMTP(host, port)
    smtp.helo(localHostName)
    smtp.ehlo(localHostName)
    smtp.starttls()
    smtp.login(user, password)
    smtp.sendmail(sender, receiver, message)
    smtp.quit()

def parseResponse(response):
    assert response[0] == 'OK'
    result = response[1][::2]
    result = [str(e[1],'utf8') for e in result]
    for e in result:
        assert e.startswith('Subject: ')
        assert e.endswith('\r\n\r\n')
    result = [e[9:-4] for e in result]
    return result
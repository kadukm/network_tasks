import os.path
import base64
import socket
import ssl


class Template:
    CRLF = '\r\n'
    TIMEOUT = 5
    MIME_TYPES = {
        '.mp3': 'audio/mpeg',
        '.pdf': 'application/pdf',
        '.zip': 'application/zip',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.txt': 'text/plain',
    }

    def __init__(self, text_path, files, theme):
        self.login = 'mk.shark25@yandex.ru'
        self.pswd = (
        	'PASSWORD'
        	)
        self.stop_symbol = '--15HmuRniMa=====OImHacfE45heReHe'
        self.header = [
            'EHLO my_test',
            'AUTH LOGIN',
            base64.b64encode(self.login.encode()).decode(),
            base64.b64encode(self.pswd.encode()).decode(),
            'MAIL FROM: {}'.format(self.login),
            None,  # addressee must be here
            'DATA']
        self.body = [
            'From: Me {}'.format(self.login),
            None,  # addressee must be here
            'Subject: {}'.format(theme),
            'Content-Type: multipart/mixed; boundary={};'.format(self.stop_symbol[2:]),
            '']
        self._add_text(text_path)
        self._add_files(files)
        self._end_body()

    def _add_text(self, text_path):
        self.body.append(self.stop_symbol)
        self.body.append('Content-Type: text/plain; charset="utf-8"')
        self.body.append('')
        with open(text_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.endswith('\n'):
                    line = line[:-1]
                if line == '.':
                    line = '..'
                self.body.append(line)

    def _add_files(self, files):
        for filepath in files:
            filename = os.path.basename(filepath)
            data, ext = self.parse_file(filepath)
            self.body += [
                self.stop_symbol,
                'Content-Type:{}; name={}'.format(self.MIME_TYPES[ext], filename),
                'Content-Transfer-Encoding:base64',
                'Content-Disposition:attachment; filename={}'.format(filename),
                '',
                base64.b64encode(data).decode()]

    def _end_body(self):
        # self.body.append('')
        self.body.append(self.stop_symbol + '--')
        self.body.append('')
        self.body.append('.')

    def _set_addressee(self, addressee):
        self.header[5] = 'RCPT TO: {}'.format(addressee)
        self.body[1] = 'To: You <{}>'.format(addressee)

    def send_to(self, addressee):
        self._set_addressee(addressee)
        sock = socket.socket()
        sock.settimeout(self.TIMEOUT)
        sock.connect(('smtp.yandex.ru', 465))
        ssl_sock = ssl.wrap_socket(sock)
        print(ssl_sock.recv(1024).decode())
        try:
            for header_line in self.header:
                self._send_to(ssl_sock, header_line)
                self._handle_sock(ssl_sock)
            for body_line in self.body:
                self._send_to(ssl_sock, body_line)
            self._handle_sock(ssl_sock)
            self._send_to(ssl_sock, 'QUIT')
            self._handle_sock(ssl_sock)
        except Exception as e:
            print("Can't send message to {} because:\n{}".format(addressee, e))
        else:
            print('Message was successfully sent')
        finally:
            ssl_sock.close()
            sock.close()

    def _send_to(self, ssl_sock, msg):
        ssl_sock.send((msg + self.CRLF).encode())
        print('SENT: {}'.format(msg if len(msg) < 800 else 'big data'))

    def _handle_sock(self, ssl_sock):
        data = ssl_sock.recv(1024)
        print('RECV: {}'.format(data.decode()))
        if data.startswith(b'4') or data.startswith(b'5'):
            raise Exception("Server can't handle this message")

    @staticmethod
    def parse_file(filepath):
        ext = os.path.splitext(filepath)[1]
        with open(filepath, 'rb') as f:
            data = f.read()
        return data, ext

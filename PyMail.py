from dotenv import load_dotenv
import socket
import base64
import os
import re
import uuid
import time
import datetime
import math
import pytz


class Mail(object):
    """docstring for Mail."""

    ### connection params ###
    __smtp_host = ''
    __smtp_port = 0
    __smtp_user = ''
    __smtp_password = ''


    __sock = ''
    useragent = 'PyMail'
    _charset		= 'utf-8'
    __newline = "\r\n"
    __content_type = 'plain'

    _header_str = ''
    _finalbody = ''

    _priorities = {
		1 : '1 (Highest)',
		2 : '2 (High)',
		3 : '3 (Normal)',
		4 : '4 (Low)',
		5 : '5 (Lowest)'
	}

    priority = 3

    ### mail attributes ###
    _from = ''
    _to = ''
    _subject = ''
    _body = ''
    _headers = {}

    ## mail server response ##
    __response = ''
    __response_code = ''

    def __init__(self, arg = None):

        self.arg = arg
        load_dotenv()
        self.intialise()



    def intialise(self):

        self.__smtp_host = os.environ.get("EMAIL_HOST")
        self.__smtp_port = int(os.environ.get("EMAIL_PORT"))
        self.__smtp_user = os.environ.get("EMAIL_HOST_USER")
        self.__smtp_password = os.environ.get("EMAIL_HOST_PASSWORD")



    def get_connection_params(self):

        print(self.__smtp_host)



    def mail_from(self, mail_from, name = ''):

        self._from = mail_from

        self._set_header('From', name + ' <' + mail_from + '>');



    def get_mail_from(self):

        print(self._from)



    def to(self, to):

        self.__to = to

        self._set_header('To', to);


    def subject(self, subject = ''):

        self.__subject = subject
        self._set_header('Subject', subject)



    def message(self, body = ''):

        self.__body = body




    def _get_hostip(self):

        try:
            return str(socket.gethostname())

        except socket.error as err:
            print("failed to resolve client ip")
            exit()



    def _get_message_id(self):

        return '<' + str(uuid.uuid1()).split('-')[0] + '@' + self._from.split('@')[1] + '>'




    def _set_date(self):

        dt = datetime.datetime.now()

        return dt.strftime('%a, %d %b %Y %H:%M:%S ') + dt.astimezone().strftime('%z')




    def _build_headers(self):

        self._set_header('X-Sender', self._headers['From'])
        self._set_header('X-Mailer', self.useragent)
        self._set_header('User-Agent', self.useragent)
        self._set_header('Date', self._set_date())
        self._set_header('X-Priority', self._priorities[self.priority])
        self._set_header('Message-ID', self._get_message_id())
        self._set_header('Mime-Version', '1.0')



    def _build_message(self):
        ## write header data
        self._write_headers()

        ## implement other content types later
        if self.__content_type == 'plain':
            add_hdr = 'Content-Type: text/html; Charset: ' + self._charset + self.__newline + 'Content-Transfer-Encoding: 8bit'
            self._finalbody = add_hdr + self.__newline + self.__newline + self.__body
            return True


    def _send_command(self, command, data = ''):

        if command == 'HELLO':
            command_extended = "EHLO " + self._get_hostip()
            resp_code = '250'

        if command == 'FROM':
            command_extended = 'MAIL FROM:<' + data + '>'
            resp_code = '250'

        if command == 'TO':
            command_extended = 'RCPT TO:<' + data + '>'
            resp_code = '250'

        if command == 'DATA':
            command_extended = 'DATA'
            resp_code = '354'

        if command == 'QUIT':
            command_extended = 'QUIT'
            resp_code = '221'

        self._send_data(command_extended)
        self._read_data()

        if self.__response_code != resp_code:
            exit("Error: " + self.__response)




    def _send_data(self, data):

        data = data + self.__newline
        try:
            sent_count = self.__sock.send(data.encode())

        except socket.error as err:
            print ("sending data to mail server failed: %s" %(err))
            exit()

        if not sent_count:
            exit("Error sending data to server")




    def _read_data(self):

        try:
            data = self.__sock.recv(1024)
            response = data.decode()

        except socket.error as err:
            print ("receiving data from mail server failed: %s" %(err))
            exit()
        print(response)
        self.__response = response
        self.__response_code = response[:3]




    def _smtp_authenticate(self):

        if not self.__smtp_user or not self.__smtp_password:
            print("Error: missing username or password")
            exit()
        self._send_data("AUTH LOGIN")
        self._read_data()

        if self.__response_code == '503': # already authenticated
            return True

        if self.__response_code != '334':
            print("Error:  failed")
            return False

        user = base64.b64encode(bytes(self.__smtp_user, 'utf-8')).decode()
        password = base64.b64encode(bytes(self.__smtp_password, 'utf-8')).decode()
        self._send_data(user)
        self._read_data()
        self._send_data(password)
        self._read_data()

        if self.__response_code != '235':
            print("Error:  authentication error")
            return False

        return True

    def _smtp_connect(self):

        if not self.__smtp_host or not self.__smtp_port:
            print("Error: missing hostname or port")
            exit()

        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.settimeout(2)
            self.__sock.connect((self.__resolve_host(), self.__smtp_port))

        except socket.error as err:
            print ("connecting to mail server failed: %s" %(err))
            exit()

        self._read_data()

        self._send_command("HELLO")



    def __resolve_host(self):

        try:
            ip_add = socket.gethostbyname(self.__smtp_host)

        except socket.gaierror:
            print ("there was an error resolving the host")
            exit()

        return ip_add



    def _set_header(self, header, value):

        value = value.replace("\n", value)
        value = value.replace("\r", value)
        self._headers[header] = value



    def _write_headers(self):

        self._header_str = ''
        for key, value in self._headers.items():
            self._header_str += key + ': ' + value + self.__newline



    def send(self):

        ## pack header attributes
        self._build_headers()

        ## establish connection to smtp server
        self._smtp_connect()

        ## Authenticate with credentials
        self._smtp_authenticate()

        ## send from command and data
        self._send_command('FROM', self._headers['From'])

        ## send RCPT command and data
        self._send_command('TO', self._headers['To'])

        ## prepare the message to send
        self._build_message()

        ## start data sending
        self._send_command('DATA')

        ## send the mail content
        self._send_data(self._header_str + re.sub(r'/^\./m', r'..$1',self._finalbody))

        ## send data completed signal
        self._send_data(".")

        ## read the final response
        self._read_data()

        if self.__response_code == '250':
            print('Mail sent successfully\n')
        else:
            print('Failed to send mail : ' + self.__response)

        self._send_command('QUIT')

        self.__sock.close()

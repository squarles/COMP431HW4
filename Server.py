#Jess Quarles (Onyen squarles)
#I pledge the UNC Honor Pledge

# SERVER

from socket import *
import sys
import re

def parse(x, socket):
    #print(x, end = "")
    global last_command
    if re.compile('^HELO[ \t]+').match(x):
        last_command = "DATA"
        helo(x, socket)
    elif re.compile('^MAIL[ \t]+FROM:.*').match(x):
        if not last_command == "DATA":
            raise UserWarning(503)
        else: mail_from(x, socket)
    elif re.compile('^RCPT[ \t]+TO:.*').match(x):
        if last_command == "DATA":
            raise UserWarning(503)
        else: rcpt_to(x, socket)
    elif re.compile('^DATA[ \t]*$').match(x):
        if not last_command == "TO":
            raise UserWarning(503)
        else: data(x, socket)
    elif re.compile('^QUIT[ \t]*$').match(x):
        send_message("221 " + gethostname() + " closing connection", socket)
        global has_quit
        has_quit = 1
        socket.close()
    else: raise UserWarning(500)

def helo(x, socket):
    y = x
    y = re.split(r'^HELO[ \t]+',y)[1]
    y = re.split(r'[ \t\n]',y)[0]
    send_message("250 Hello " + y + " pleased to meet you", socket)

def mail_from(x, socket):
    y = x
    y = re.split(r'^MAIL[ \t]+FROM:',y)[1]
    y = nullspace(y)
    y = path(y)
    y = CRLF(y)
    global last_command
    last_command = "FROM"
    output = "From: <" + x.split("<")[1].split(">")[0] + ">\n"
    #global content
    #content += output
    send_message("250 OK", socket)

def rcpt_to(x, socket):
    y = x
    y = re.split(r'^RCPT[ \t]+TO:',y)[1]
    y = nullspace(y)
    y = path(y)
    y = CRLF(y)
    address = x.split("<")[1].split(">")[0]
    global last_command
    last_command = "TO"
    output = "To: <" + address + ">\n"
    domain = address.split("@")[1]
    #global content
    #content += output
    global recipients
    if domain not in recipients.split('\n'):
        recipients += domain
        recipients += "\n"
    send_message("250 OK", socket)

def data(x, socket):
    y = x
    if not re.compile('^DATA[ \t]*$').match(y):
        raise UserWarning(500)
    global last_command
    last_command = "DATA"
    send_message("354 Start mail input; end with <CRLF>.<CRLF>", socket)
    global content
    global recipients
    done = 0
    while not done:
        text = receive_message(socket)
        lines = text.split("\n")
        while(len(lines) != 0):
            current_line = lines.pop(0)
            if (current_line == "."):
                done = 1
            else:
                content += current_line + "\n"
    paths = recipients.split("\n")
    for path in paths:
        if path:
            try:
                file_path = "/home/squarles/HW4/forward/" + path
                file = open(file_path, 'a')
                file.write(content)
                file.close()
            except IOError:
                print("File error")
                sys.exit()
    content = ""
    recipients = ""
    send_message("250 OK", socket)

def whitespace(x):
    if not re.compile('^[ \t]+').match(x):
        raise UserWarning(500)
    return re.split(r'^[ \t]+', x)[1]

def nullspace(x):
    if not re.compile('^[ \t]+').match(x):
        return x
    return re.split(r'^[ \t]+', x)[1]

def path(x):
    y = x
    if not re.compile('^<').match(y):
        raise UserWarning(501)
    y = re.split(r'^<', y)[1]
    y = mailbox(y)
    if not re.compile('^>').match(y):
        raise UserWarning(501)
    y = re.split(r'^>', y)[1]
    return y

def mailbox(x):
    y = x
    y = local_part(y)
    if not re.compile('^@').match(y):
        raise UserWarning(501)
    y = re.split(r'^@', y)[1]
    y = domain(y)
    return y

def local_part(x):
    if not re.compile('^[^ \t<>()\[\]\\.,;:@\"]+').match(x):
        raise UserWarning(501)
    return re.split(r'^[^ \t<>()\[\]\\.,;:@\"]+', x)[1]

def domain(x):
    y = x
    y = element(y)
    while re.compile('^\.').match(y):
        y = re.split(r'^\.', y)[1]
        y = element(y)
    return y

def element(x):
    if not re.compile('^[a-zA-Z][a-zA-Z0-9]*').match(x):
        raise UserWarning(501)
    return re.split(r'^[a-zA-Z][a-zA-Z0-9]*', x)[1]

def CRLF(x):
    if not re.compile('^[ \t]*$').match(x):
        raise UserWarning(501)
    return x

def send_message(message, socket):
    message_text = message + "\n"
    #print("SERVER: {" + message_text + "}")
    socket.send(message_text.encode())

def receive_message(socket):
    decoded = socket.recv(2048).decode()
    #print("CLIENT: {" + decoded + "}")
    decoded = re.split(r'\n$', decoded)[0]
    return decoded

def greet(socket):
    send_message("220 " + gethostname(), socket)

try:
    serverPort = int(sys.argv[1])#10397
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
except OSError:
    print("Port bind error")
    sys.exit()
serverSocket.listen(1)
#print("Server ready")

last_command = None
content = ""
recipients = ""
has_quit = 0

while True:
    try:
        connectionSocket, addr = serverSocket.accept()
        has_quit = 0
        greet(connectionSocket)
        while not has_quit:
            message = receive_message(connectionSocket)
            try: parse(message, connectionSocket)
            except UserWarning as w:
                last_command = "DATA"
                content = ""
                errorMsg = "Oops! This error message shouldn't be possible!"
                if w.args[0] == 500:
                    errorMsg = "500 Syntax error: command unrecognized"
                elif w.args[0] == 501:
                    errorMsg = "501 Syntax error in parameters or arguments"
                elif w.args[0] == 503:
                    errorMsg = "503 Bad sequence of commands"
                send_message(errorMsg, connectionSocket)
    except ConnectionError:
        print("There was a connection error")
    finally:
        last_command = None
        content = ""
        recipients = ""
        has_quit = 0

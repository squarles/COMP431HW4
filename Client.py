#Jess Quarles (Onyen squarles)
#I pledge the UNC Honor Pledge

# CLIENT

from socket import *
import sys
import re

def parse(text, socket):
    lines = text.split('\n')
    sender = lines[0].split("From: ")[1]
    send_message("MAIL FROM: " + sender, socket)
    if not re.compile('^250 .*$').match(receive_message(socket)):
        raise UserWarning("")
    recipients = re.split('^To: ', lines[1])[1].split(", ")
    for address in recipients:
        send_message("RCPT TO: " + address, socket)
        if not re.compile('^250 .*$').match(receive_message(socket)):
            raise UserWarning("")
    send_message("DATA", socket)
    if not re.compile('^354 .*$').match(receive_message(socket)):
        raise UserWarning("")
    response = ""
    #for line in lines:
    send_message(text, socket)
    if not re.compile('^250 .*$').match(receive_message(socket)):
        raise UserWarning("")

def send_message(message, socket):
    message_text = message + "\n"
    #print("CLIENT: {" + message_text + "}")
    socket.send(message_text.encode())

def receive_message(socket):
    decoded = socket.recv(2048).decode()
    #print("SERVER: {" + decoded + "}")
    decoded = re.split(r'\n$', decoded)[0]
    return decoded

def generate_email():
    text = ""
    sender_validated = 0
    while not sender_validated:
        sender = input("From:\n")
        try:
            validate_email_address(sender)
            text += "From: <" + sender + ">\n"
            sender_validated = 1
        except UserWarning:
            print("An invalid email address was entered. Please try again.")
    recipients_validated = 0
    while not recipients_validated:
        recipients = re.split(r',[ \t]*',input("To:\n"))
        try:
            for address in recipients:
                validate_email_address(address)
            text += "To: <" + ">, <".join(recipients) + ">\n"
            recipients_validated = 1
        except UserWarning:
            print("An invalid email address was entered. Please try again.")
    text += "Subject: " + input("Subject:\n") + "\n"
    next_line = input("Message:\n")
    while next_line != ".":
        text += "\n"
        text += next_line
        next_line = input()
    text += "\n."
    return text

def validate_email_address(x):
    y = x
    y = local_part(y)
    if not re.compile('^@').match(y):
        raise UserWarning()
    y = re.split(r'^@', y)[1]
    y = domain(y)
    if(y):
        raise UserWarning()

def local_part(x):
    if not re.compile('^[^ \t<>()\[\]\\.,;:@\"]+').match(x):
        raise UserWarning()
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
        raise UserWarning()
    return re.split(r'^[a-zA-Z][a-zA-Z0-9]*', x)[1]

serverName = sys.argv[1]
serverPort = int(sys.argv[2]) #10397
clientSocket = socket(AF_INET, SOCK_STREAM)

text = generate_email()
#print("[" + text + "]")

try:
    clientSocket.connect((serverName, serverPort))
    #send_message("...", clientSocket)
    greeting = receive_message(clientSocket)
    send_message("HELO " + gethostname(), clientSocket)
    greeting2 = receive_message(clientSocket)
    try: parse(text, clientSocket)
    except UserWarning:
        print("SMTP protocol error encountered")
    finally:
        send_message("QUIT", clientSocket)
        receive_message(clientSocket)
    #clientSocket.close()
except ConnectionError as e:
    print(e)
    print("There was a problem with the socket")
finally:
    pass #print("Connection closed")

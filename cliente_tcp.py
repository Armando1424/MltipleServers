import socket
import pickle
import errno
import sys

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 40000
myEncode = 'utf-8'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

def receive_message(clientSocket):
    try:
        message_header = clientSocket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False

        message_length = int(message_header.decode(myEncode).strip())
        message = pickle.loads(clientSocket.recv(message_length))
        message['header'] = message_header
        return message

    except:
        return False

def sendToServer(message):
    msg = pickle.dumps(message)
    msg = bytes(f'{len(msg):<{HEADER_LENGTH}}',myEncode) + msg
    client_socket.sendto(msg, (IP,PORT))

message = dict(type = "client")
sendToServer(message)
canSend = False

while True:
    
    if canSend:
        text1 = ""
        text2 = ""

        option = int(input("Ingrese el numero de la operacion que va a realizar: "))
        if option == 1:
            message['service'] = "add"
            text1 = "Ingrese el primer numero "
            text2 = "Ingrese el segundo numero "
        elif option == 2:
            message['service'] = "subtract"
            text1 = "Ingrese el primer numero "
            text2 = "Ingrese el segundo numero "
        elif option == 3:
            message['service'] = "multiply"
            text1 = "Ingrese el multiplicando "
            text2 = "Ingrese la multiplicador "
        elif option == 4:
            message['service'] = "divide"
            text1 = "Ingrese el Dividendo "
            text2 = "Ingrese el Divisor "
        elif option == 5:
            message['service'] = "power"
            text1 = "Ingrese el numero "
            text2 = "Ingrese la potencia "
        message['val1'] = float(input(text1))
        message['val2'] = float(input(text2))
        sendToServer(message)
        canSend = False
        

    try:
        while True:   

            message = receive_message(client_socket)
            if message:
                print(message['result'])
                canSend = True
            break        
            

    except IOError as e:
        if e.errno != errno.EAGAIN or e.errno != errno.EWOULDBLOCK:
            print('Reading error',str(e))
            sys.exit()
        continue

    except Exception as e:
        print('general error', str(e))
        sys.exit()
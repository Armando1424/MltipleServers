import socket
import select
import pickle

HEADER_LENGTH = 10
address = dict( serverope = ("127.0.0.1", 40000),
                serveradd = ("127.0.0.1", 40004))

myEncode = 'utf-8'
firstConnection = True

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srevero_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
srevero_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)

server_socket.bind(address['serveradd']) 
server_socket.listen()


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

print("Servidor Listo")

while True:
    client_socket,client_address = server_socket.accept()
    while True:
        message = receive_message(client_socket)
        if message is False:
            continue
        
        if firstConnection:
            srevero_socket.connect(address['serverope'])
            firstConnection = False
        
        print(f"Nuevo cliente: {client_address[0]}:{client_address[1]}")
        message['type'] = "server"
        message['result'] = message['val1'] / message['val2']

        msg = pickle.dumps(message)
        msg = bytes(f'{len(msg):<{HEADER_LENGTH}}',myEncode) + msg
        srevero_socket.sendto(msg, client_address)


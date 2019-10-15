import socket
import select
import pickle

HEADER_LENGTH = 10
address = dict( serverope = ("127.0.0.1", 40000),
                serveradd = ("127.0.0.1", 40001),
                serversub = ("127.0.0.1", 40002),
                servermul = ("127.0.0.1", 40003),
                serevrdiv = ("127.0.0.1", 40004),
                serverpow = ("127.0.0.1", 40005))
myEncode = 'utf-8'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
add_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sub_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mul_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
div_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pow_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
add_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
sub_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
mul_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
div_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
pow_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)


server_socket.bind(address['serverope'])
server_socket.listen()

#add_socket.connect(address['serveradd'])
sub_socket.connect(address['serversub'])
#mul_socket.connect(address['servermul'])
#div_socket.connect(address['serevrdiv'])
#pow_socket.connect(address['serverpow'])


sockets_list = [server_socket]

clients = {}
servers = {}

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
    server_addres = ()
    mysocket = server_socket
    if message['service'] == "add":
        server_addres = address['serveradd']
        mysocket = add_socket
    elif message['service'] == "subtract":
        server_addres = address['serversub']
        mysocket = sub_socket
    elif message['service'] == "multiply":
        server_addres = address['servermul']
        mysocket = mul_socket
    elif message['service'] == "divide":
        server_addres = address['serevrdiv']
        mysocket = div_socket
    elif message['service'] == "power":
        server_addres = address['serverpow']
        mysocket = pow_socket

    msg = pickle.dumps(message)
    msg = bytes(f'{len(msg):<{HEADER_LENGTH}}',myEncode) + msg
    mysocket.sendto(msg,server_addres)

def sendToClient(message):
    msg = pickle.dumps(message)
    msg = bytes(f'{len(msg):<{HEADER_LENGTH}}',myEncode) + msg
    print("enviando mensaje a: " + str(message['clAddr'][1]))
    listClients = clients.values()
    for client in listClients:
        if client['clAddr'][1] == message['clAddr'][1]:
            key = list(clients.keys())[list(clients.values()).index(client)]
            key.sendto(msg,message['clAddr'])
            break
        

print("Servidor Listo")

while True:
    read_sockets, _, exception_sockts = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket,client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)

            if user['type'] == "server":
                print(f"Nuevo server: {client_address[0]}:{client_address[1]}")
                servers[client_socket] = user
                user['result'] ="Resultado: " + str(user['result'])
                sendToClient(user)

            else:
                print(f"Nuevo cliente: {client_address[0]}:{client_address[1]}")
                user['clAddr'] = client_address
                clients[client_socket] = user
                msg = "Menu:\n1->Suma\n2->resta\n3->Multiplicacion\n4->Divicion\n5->Potencia"
                user['result'] = msg
                sendToClient(user)  
                            

        else:
            message = receive_message(notified_socket)

            if notified_socket in servers:
                if message is False:
                    sockets_list.remove(notified_socket)
                    del servers[notified_socket]
                    continue

                message['result'] ="Resultado: " + str(message['result'])
                sendToClient(message)

            else:
                if message is False:
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                    
                sendToServer(message)

    for notified_socket in exception_sockts:
        sockets_list.remove(notified_socket)
        if notified_socket in servers:
            del servers[notified_socket]
        else:
            del clients[notified_socket]

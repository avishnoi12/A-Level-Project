import threading
import socket
import test

PORT = 9090
HOST = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"
clients = []
socketExists = False

def createNewServer():
    global Server, recieveThread, socketExists

    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating the socket
    Server.bind((HOST, PORT)) #creating the server
    Server.listen() #listening for connections
    socketExists = True

    print(f"[SERVER RUNNING] ip: {HOST}")
    recieveThread = threading.Thread(target=receive) #creating the recieve thread
    recieveThread.start() #starting the thread

def broadcast(message, sender):
    print(f"[BROADCASTING] {message.decode(FORMAT)}")
    for client in clients: #sending message to all other clients but sender
        if client != sender:
                client.send(message)

def handle(Client):
    while True:
        try:
            message = Client.recv(1024) #receiving the mesasge for the client
            broadcast(message, Client) #outputting message to all clients
            print(message.decode(FORMAT))
        except:
            clients.remove(Client) #remove clients from array
            Client.close() #closing the clent
            break

def receive():
    while True:
        Client, address = Server.accept() #accepting the client
        clients.append(Client) #adding the client to the clients array
        print(f"Connected with {address}")
        Client.send("Connected with server".encode(FORMAT))
        
        thread = threading.Thread(target=handle, args=(Client,)) #creating the handle thread
        thread.start()

def serverExists():
    return socketExists
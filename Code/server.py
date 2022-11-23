import threading
import socket
import gameplay

PORT = 9090
HOST = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"
clients = []

def createNewServer():
    global Server, socketExists, recieveThread

    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating the socket
    #Server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    Server.bind((HOST, PORT)) #creating the server
    Server.listen() #listening for connections
    socketExists = True

    print(f"[SERVER RUNNING] ip: {HOST}")
    recieveThread = threading.Thread(target=receive) #creating the recieve thread
    recieveThread.start() #starting the thread

def broadcast(message, sender):
    #print(f"[BROADCASTING] {message.decode(FORMAT)}")
    for client in clients: #sending message to all other clients but sender
        if client != sender:
                client.send(message)

def handle(Client):
    while True:
        try:
            message = Client.recv(1024) #receiving the mesasge from the client
            if message.decode(FORMAT) == "READY":
                #sending the new client the details of the allPlayers array
                playerInfo = str(gameplay.playerInfo())
                Client.send(playerInfo.encode(FORMAT))
                newDetails = Client.recv(1024) #recieving the clients details
                broadcast(newDetails, Client)
            else:
                #print("[SERVER] recieved: "+message.decode(FORMAT))
                broadcast(message, Client) #outputting message to all clients
        except:
            clients.remove(Client) #remove clients from array
            Client.close() #closing the clent
            break

def receive():
    while True:
        Client, address = Server.accept() #accepting the client
        clients.append(Client) #adding the client to the clients array
        print(f"Connected with {address}")

        thread = threading.Thread(target=handle, args=(Client,)) #creating the handle thread
        thread.start() #starting thread

def closeServer():
    try: #validation
        #Server.shutdown(socket.SHUT_RDWR)
        Server.close()
        for client in clients:
            client.close()
        print("Closed server")
    except:
        print("Error occured")

def serverExists():
    if 'socketExists' in globals():
        return True
    else:
        return False
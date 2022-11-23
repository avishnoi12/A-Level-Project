import socket
import threading
import ast
import gameplay

PORT = 9090
FORMAT = "utf-8"

def connectToServer(HOST):
    global Client, recieveThread, socketExists

    Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating a client
    Client.connect((HOST, PORT)) #connecting the client to the server
    socketExists = True

    recieveThread = threading.Thread(target=recieve) #creating the recieving thread
    recieveThread.start() #starting the thread

def recieve():
    while True:
        try:
            message = Client.recv(1024).decode(FORMAT) #recieving the message
            #print("[CLIENT] recieved: "+message)
            message = ast.literal_eval(message)
            gameplay.decodeMessage(message)
        except:
            Client.close() #if the client no longer exists
            break

def sendMessage(message):
    #print("[CLIENT] sends: "+message.decode(FORMAT))
    Client.send(message) #sending the client the message

def clientExists():
    if 'socketExists' in globals():
        return True
    else:
        return False

def getClient():
    return Client


import socket
import threading
import json
import test

PORT = 9090
FORMAT = "utf-8"
socketExists = False

def connectToServer(HOST):
    global Client, socketExists,  recieveThread

    Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating a client
    Client.connect((HOST, PORT)) #connecting the client to the server
    socketExists = True

    recieveThread = threading.Thread(target=recieve) #creating the recieving thread
    recieveThread.start() #starting the thread

def recieve():
    while True:
        try:
            message = Client.recv(1024).decode(FORMAT) #recieving the message
            print(message)
            test.displayMessage(message)
        except:
            Client.close() #if the client no longer exists
            break

def sendMessage(message):
    Client.send(message) #sending the client the message

def clientExists():
    return socketExists

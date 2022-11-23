
from functools import partial
import threading
import tkinter as tk
from tkinter import END, Button, ttk
from PIL import Image, ImageTk
import server as srvr
import client as clnt
import time
import socket

HOST = socket.gethostbyname(socket.gethostname())

animateCount = 0
class Player(object):
    def __init__(self, name) -> None:
        self.name = name
        self.bal = 20

    def bark(self):
        print(self.name)

class AI(Player):
    def __init__(self, name, type) -> None:
        super().__init__(name)
        self.type = type

    def bark(self):
        super().bark()
        print("This also")
    
    def woof(self):
        super().bark()

def animate(canvas, id, startx, starty, x, y):
    xStep = (x-startx)//10
    yStep = (y-starty)//10
    anim(canvas, id, xStep, yStep, x, y)
    
def anim(canvas, id, xstep, ystep, x, y):
    global animateCount
    if animateCount < 10:
        canvas.move(id, xstep, ystep)
        animateCount += 1
        canvas.after(20, anim, canvas, id, xstep, ystep, x, y)
    elif animateCount == 10:
        animateCount = 0
        canvas.coords(id, x, y)

def a(num):
    if num >= 10:
        return
    else:
        print("hello")
    print("hi")

def connectToSever():
    if serverIP.get() != "":
        HOST = serverIP.get()
        try:
            clnt.connectToServer(HOST)
        except:
            print("Cannot connect")
        else:
            serverIP.delete(0, END)

def createServer():
    try:
        srvr.createNewServer()
    except:
        print("Cannot create server")
    else:
        #create a client
        clnt.connectToServer(HOST)
    
def displayMessage(message):
    #msgLabel.configure(text=message)
    msgLabel = tk.Label(window, text=message)
    msgLabel.pack(pady=5) 

def sendMsg():
    msg = messageEntry.get()
    msg = msg.encode("utf-8")
    clnt.sendMessage(msg)

def doesExist():
    if srvr.serverExists():
        print("Exists!")

def run():
    global createServerBtn, joinServer, serverIP, messageEntry, confirmBtn, msgLabel, window
    window = tk.Tk()
    window.geometry("300x400")

    createServerBtn = tk.Button(window, text="Create", command=createServer)
    createServerBtn.pack(pady=10)

    joinServer = tk.Button(window, text="join", command=connectToSever)
    serverIP = tk.Entry(window)
    serverIP.pack(pady=10)
    joinServer.pack(pady=10)

    messageEntry = tk.Entry(window)
    messageEntry.pack(pady=10)

    confirmBtn = tk.Button(window, text="Send", command=sendMsg)
    confirmBtn.pack(pady=10)

    doesExistButton = tk.Button(window, text="Exist?", command=doesExist)
    doesExistButton.pack(pady=30)

    window.mainloop()

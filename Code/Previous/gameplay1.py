#Pocket Aces gameplay
#Date started 10/12/21
#Last edited 10/12/21

#?Pop up screen - feature not available in thie current prototype

#! imports
from os import read
from library import *
import newGame
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

def openNewGame(window, event):
    buttonPressSound.play()
    canvas.destroy()
    newGame.runNewGame(window)
    exit()

def runGameplay(window):
    global canvas, popUp, okButton

    print("Running gameplay...")
    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.pack()
    
    #*Creating the background image
    bgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/titleBackground.png")) #path
    bg = canvas.create_image(0, 0, image=bgImage, anchor=tk.NW)

    #*Logo
    logoImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/circleLogo.fw.png")) #path
    logo = canvas.create_image(0, 0, image=logoImage, anchor=tk.NW)

    popUp = newPopUp(canvas, "This feature is unavailable\nin this prototype")

    #*Buttons
    newGameFunc = partial(openNewGame, window)
    okButton = newButton(canvas, 780, 660, "greenButton.fw.png", "popUp", newGameFunc)
    okButton.addLabel(canvas, "OK", "white", (895,700), 30, "popUp", newGameFunc)

    window.mainloop()
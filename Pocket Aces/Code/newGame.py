#Pocket Aces v1.1
#Date started 01/12/21
#Last Date edited 01/12/21

#!imports
import pygame
from pygame.constants import GL_CONTEXT_PROFILE_COMPATIBILITY
from library import *
import titleScreen
import threading
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

def stackUpdate(event):
    #updating label for volume
    labelText = str(startStackscale.get()) + "BIG BLINDS"
    canvas.itemconfigure(startStackLabel, text=labelText)

def openTitleScreen(window, event):
    #clicked 'leave' on the pop up screen
    buttonPressSound.play() #playijng button press sound
    canvas.destroy()
    #os.system('py main.py')
    titleScreen.runTitleScreen(window)
    exit()

def joinGame(event):
    pass

def loadGame(event):
    pass

def createGame(event):
    pass

def runNewGame(window):
    global maxPlayersButton, gameTypeButton, AILevelButton, assistsButton, startStackscale, startStackLabel, canvas

    print("Rnning new game...")
    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.pack()

    #*Creating the background image
    bgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/titleBackground.png")) #path
    bg = canvas.create_image(0, 0, image=bgImage, anchor=tk.NW)

    #*Logo
    logoImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/circleLogo.fw.png")) #path
    logo = canvas.create_image(0, 0, image=logoImage, anchor=tk.NW)

    titleImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/newGameText.fw.png"))
    screenTitle = canvas.create_image(430,130, image=titleImage, anchor=tk.NW)

    #*RadioButtons
    maxPlayersButton = newRadioButton(canvas, 700, 330, ["6","9"], ("newGame"), "Settings.json", ("options","MaxPlayer"))

    gameTypeButton = newRadioButton(canvas, 700, 630, ["SINGLE","MULTI"], ("newGame"), "Settings.json", ("options","GameType"))

    AILevelButton = newRadioButton(canvas, 700, 780, ["NOVICE","PRO", "EXPERT"], ("newGame"), "Settings.json", ("options","AI Level"))

    assistsButton = newRadioButton(canvas, 700, 930, ["ON","OFF"], ("newGame"), "Settings.json", ("options","Assists"))

    #*starting stack slider
    startStackscale = tk.Scale(canvas, from_=5, to=50, orient=tk.HORIZONTAL, font=(FONTNAME,20), bg=TERTARYCOLOUR, activebackground="white"
        ,length=380, troughcolor=PRIMARYCOLOUR, sliderlength=20, command=stackUpdate, showvalue=0, width=20)
    startStackscale.set(getJson("Settings.json",("options","StartStack")))
    startStackscale.place(x=700,y=480)
    startStackLabel = canvas.create_text(1200,480, text=str(startStackscale.get())+"BIG BLINDS",fill="white",font=(FONTNAME,30))

    #*Buttons
    cancelFunc = partial(openTitleScreen, window)
    cancelButton = newButton(canvas, 65, 915, "redButton.fw.png", None, cancelFunc)
    cancelButton.addLabel(canvas, "CANCEL", "white", (180,960), 30, None, cancelFunc)

    createGameButton = newButton(canvas, 1610, 915, "greenLargeButton.fw.png", None, createGame)
    createGameButton.addLabel(canvas, "CREATE\nGAME", "white", (1750, 965), 30, None, createGame)

    joinGameButton = newButton(canvas, 1320, 915, "tealButton.fw.png", None, joinGame)
    joinGameButton.addLabel(canvas, "JOIN\nGAME", "white", (1460, 965), 30, None, joinGame)

    loadGameButton = newButton(canvas, 1030, 915, "tealButton.fw.png", None, loadGame)
    loadGameButton.addLabel(canvas, "LOAD\nGAME", "white", (1170, 965), 30, None, loadGame)

    #*Labels
    maxPlayersLabel = newOptionLabel(canvas, 360, 310, "MAXIMUM\nPLAYERS:")

    stackLabel = newOptionLabel(canvas, 360, 460, "STARTING STACK:")

    gameTypeLabel = newOptionLabel(canvas, 360, 610, "GAME TYPE:")

    AILevelLabel = newOptionLabel(canvas, 360, 760, "AI LEVEL:")

    assistsLabel = newOptionLabel(canvas, 360, 910, "ASSISTS\nALLOWED:")

    if gameTypeButton.get() == "MULTI":
        AILevelButton.greyOrUngrey(canvas, True)
        assistsButton.greyOrUngrey(canvas, False)
    else:
        AILevelButton.greyOrUngrey(canvas, False)
        assistsButton.greyOrUngrey(canvas, True)

    window.mainloop()

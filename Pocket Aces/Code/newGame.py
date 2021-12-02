#Pocket Aces v1.1
#Date started 01/12/21
#Last Date edited 01/12/21

#!imports
import pygame
from library import *
import titleScreen
import threading
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial


def openTitleScreen(window, event):
    #clicked 'leave' on the pop up screen
    buttonPressSound.play() #playijng button press sound
    canvas.destroy()
    #os.system('py main.py')
    titleScreen.runTitleScreen(window)
    exit()

def runNewGame(window):
    global canvas
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
    maxPlayersButton = newRadioButton(canvas, 700, 330, ["6","9"], ("newGame"), "MaxPlayer")

    gameTypeButton = newRadioButton(canvas, 700, 630, ["SINGLE","MULTI"], ("newGame"), "GameType")

    AILevelButton = newRadioButton(canvas, 700, 780, ["NOVICE","PRO", "EXPERT"], ("newGame"), "AI Level")

    assistsButton = newRadioButton(canvas, 700, 930, ["ON","OFF"], ("newGame"), "Assists")

    #*Buttons
    cancelFunc = partial(openTitleScreen, window)
    cancelButton = newButton(canvas, 65, 915, "cancel.fw.png", None, cancelFunc)

    #*Labels
    maxPlayersLabel = newOptionLabel(canvas, 360, 310, "MAXIMUM\nPLAYERS:")

    gameTypeLabel = newOptionLabel(canvas, 360, 460, "GAME TYPE:")

    AILevelLabel = newOptionLabel(canvas, 360, 610, "AI LEVEL:")

    assistsLabel = newOptionLabel(canvas, 360, 760, "ASSISTS\nALLOWED:")

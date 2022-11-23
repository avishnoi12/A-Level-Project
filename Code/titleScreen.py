#Pocket Aces v1.1
#Date started 01/12/21
#Last Date edited 10/12/21

#!imports
import pygame
from library import *
import settings
import newGame
import tutorial
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

#!subprograms
def quitGame(window, event):
    global leaveButton, stayButton, popUp
    #*QUIT button pressed
    buttonPressSound.play() #playing button press sound
    popUp = newPopUp(canvas,"Are you sure you want to leave?") #creating a pop up
    
    #*Creating buttons
    leaveFunc = partial(exitGame, window)
    leaveButton = newButton(canvas, 500, 660, "redButton.fw.png", "popUp", leaveFunc)
    leaveButton.addLabel(canvas, "LEAVE", "white", (615, 700), 30, "popUp", leaveFunc)

    stayButton = newButton(canvas, 1050, 660, "greenButton.fw.png", "popUp", closePopUp)
    stayButton.addLabel(canvas, "STAY", "white", (1165,700), 30, "popUp", closePopUp) 

def openSettings(window, event):
    #*SETTINGS button pressed
    buttonPressSound.play() #playing button press sound
    canvas.destroy()
    settings.runSettings(window) #Creating settings screen
    exit()

def openNewGame(window, event):
    #*PLAY GAME button pressed
    buttonPressSound.play() #playing button press sound
    canvas.destroy()
    newGame.runNewGame(window) #Creating new game screen
    exit()

def openTutorial(window, event):
    #*TUTORIALS button pressed
    buttonPressSound.play() #playing button press sound
    canvas.destroy()
    tutorial.runTutorial(window) #Creating tutorial screen
    exit()

def closePopUp(event):
    #*STAY button pressed on pop up
    buttonPressSound.play() #playing button press sound
    canvas.delete("popUp") #deleting pop up

#!main program
def runTitleScreen(window):
    global canvas

    print("Running Title Screen...")

    #*configuring settings
    #Volume settings
    settingsVolume = (getJson("Settings.json",("settings","Volume")))/100
    pygame.mixer.music.set_volume(round(settingsVolume,2))
    buttonPressSound.set_volume(round(settingsVolume,2))

    #Fullscreen settings
    if getJson("Settings.json",("settings","FullScreen")) == "ON":
        window.attributes("-fullscreen", True) #setting to fullscreen
    else:
        window.attributes("-fullscreen", False) #setting to windowed

    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.pack()
    
    #!Images
    #*Creating the background image
    bgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/titleBackground.png")) #path
    bg = canvas.create_image(0, 0, image=bgImage, anchor=tk.NW)

    #*Logo
    logoImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/Logo.png")) #path
    logo = canvas.create_image(0, 0, image=logoImage, anchor=tk.NW)

    #*Play block
    blockImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/playBlock.fw.png")) #path
    playBlock = canvas.create_image(213, 293, image=blockImage, anchor=tk.NW)

    #*Chips image
    chipsImage = ImageTk.PhotoImage(Image.open("../Entities/Chips/pokerStacks.fw.png")) #path
    chipsIcon = canvas.create_image(425, 415, image=chipsImage, anchor=tk.NW)

    #*Limit hold'em Label
    holdemImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/holdemText.fw.png")) #path
    holdemLabel = canvas.create_image(375, 350, image=holdemImage, anchor=tk.NW)

    #!Buttons
    #*Quit button
    quitGameFunc = partial(quitGame, window)
    quitButton = newButton(canvas, 855,795,"TitleScreen/optionButton.fw.png",("title"),quitGameFunc)
    quitButton.addLabel(canvas, "QUIT","white",(1085,865),30,("title"),quitGameFunc)

    #*Settings button
    settingsFunc = partial(openSettings, window)
    settingsButton = newButton(canvas, 954,295,"TitleScreen/optionButton.fw.png",("title"),settingsFunc)
    settingsButton.addLabel(canvas, "SETTINGS","white",(1184,365),30,("title"),settingsFunc)

    #*Tutorials button
    tutorialFunc = partial(openTutorial, window)
    tutorialsButton = newButton(canvas, 905,545,"TitleScreen/optionButton.fw.png",("title"),tutorialFunc)
    tutorialsButton.addLabel(canvas, "TUTORIALS","white",(1135,615),30,("title"),tutorialFunc)

    #*Play button
    newGameFunc = partial(openNewGame, window)
    playButton = newButton(canvas, 285,735,"TitleScreen/playButton.fw.png",("title"), newGameFunc)
    playButton.addLabel(canvas, "PLAY NOW",SECONDARYCOLOUR,(515,805),30,("title"), newGameFunc)

    window.mainloop()
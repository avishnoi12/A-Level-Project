#Pocket Aces v1.1
#Date started 01/12/21
#Last Date edited 10/12/21

#!imports
from tkinter.constants import END
from library import *
import titleScreen
import gameplay
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

def stackUpdate(event):
    #*Updating label for volume
    labelText = str(startStackscale.get()) + " BIG BLINDS"
    canvas.itemconfigure(startStackLabel, text=labelText)

def openTitleScreen(window, event):
    #*CANCEL button pressed
    buttonPressSound.play()
    canvas.destroy()
    titleScreen.runTitleScreen(window)
    exit()

def updateOptions():
    #creating json string with new settings
    obj = readJson("Settings.json")
    obj["options"]["MaxPlayer"] = maxPlayersButton.get()
    obj["options"]["StartStack"] = startStackscale.get()
    obj["options"]["Assists"] = assistsButton.get()
    obj["options"]["AI Level"] = AILevelButton.get()
    obj["options"]["GameType"] = gameTypeButton.get()

    settingsFile = open("Settings.json","w")
    json.dump(obj, settingsFile, indent = 2) #writing new settings to json file
    settingsFile.close()

def openGameplay(window, event):
    buttonPressSound.play()
    updateOptions() #updating options
    canvas.destroy()
    gameplay.createGameplay(window)
    exit()

def joinGame(window, event):
    global popUp, entryBox, goButton, cancelButton

    buttonPressSound.play()
    #*creating pop up
    popUp = newPopUp(canvas, "Enter room code:")

    #*hiding scale
    startStackscale.place_forget()

    #*Creating entry box
    entryBox = tk.Entry(canvas, font=(FONTNAME, 30), justify=CENTER, fg="white", bg="grey")
    entryBox.place(x=640, y=570)

    #*Buttons
    closeFunc = partial(closePopUp, entryBox)
    cancelButton = newButton(canvas, 500, 660, "redButton.fw.png", "popUp", closeFunc)
    cancelButton.addLabel(canvas, "CANCEL", "white", (615,700), 30, "popUp", closeFunc) 

    openFunc = partial(openGameplay, window)
    goButton = newButton(canvas, 1050, 660, "greenButton.fw.png", "popUp", openFunc)
    goButton.addLabel(canvas, "GO", "white", (1165, 700), 30, "popUp", openFunc)

def loadGame(window, event):
    global listb, popUp, cancelButton, loadSaveButton

    buttonPressSound.play()
    #*creating pop up
    popUp = newPopUp(canvas, "Choose save:")

    #*hiding scale
    startStackscale.place_forget()

    #*Creating listbox with all save files
    listb = tk.Listbox(canvas, bg="grey", fg="white", width=40, height=5, font=(FONTNAME,25), bd=0, justify=CENTER,
    selectforeground=SECONDARYCOLOUR, selectbackground="white")
    for file in os.listdir("Saves/"): #repeating through every save file
        file = file.replace(".json","")
        listb.insert(END, file)
    listb.place(x=500,y=450)

    #*Buttons
    openFunc = partial(openGameplay, window)
    loadSaveButton = newButton(canvas, 1050, 660, "greenButton.fw.png", "popUp", openFunc)
    loadSaveButton.addLabel(canvas, "LOAD", "white", (1165,700), 30, "popUp", openFunc) 

    closeFunc = partial(closePopUp, listb)
    cancelButton = newButton(canvas, 500, 660, "redButton.fw.png", "popUp", closeFunc)
    cancelButton.addLabel(canvas, "CANCEL", "white", (615,700), 30, "popUp", closeFunc) 

def closePopUp(toBeDeleted, event):
    buttonPressSound.play()
    canvas.delete("popUp")
    startStackscale.place(x=700,y=480)
    toBeDeleted.destroy()

#!main function
def runNewGame(window):
    global maxPlayersButton, gameTypeButton, AILevelButton, assistsButton, startStackscale, startStackLabel, canvas

    print("Running new game...")
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
    startStackscale.place(x=700,y=500)
    startStackLabel = canvas.create_text(900,550, text=str(startStackscale.get())+" BIG BLINDS",fill="white",font=(FONTNAME,30))

    #*Buttons
    cancelFunc = partial(openTitleScreen, window)
    cancelButton = newButton(canvas, 65, 915, "redButton.fw.png", None, cancelFunc)
    cancelButton.addLabel(canvas, "CANCEL", "white", (180,960), 30, None, cancelFunc)

    openFunc = partial(openGameplay, window)
    createGameButton = newButton(canvas, 1610, 915, "greenLargeButton.fw.png", None, openFunc)
    createGameButton.addLabel(canvas, "CREATE\nGAME", "white", (1750, 965), 30, None, openFunc)

    joinFunc = partial(joinGame, window)
    joinGameButton = newButton(canvas, 1320, 915, "tealButton.fw.png", None, joinFunc)
    joinGameButton.addLabel(canvas, "JOIN\nGAME", "white", (1460, 965), 30, None, joinFunc)

    loadFunc = partial(loadGame, window)
    loadGameButton = newButton(canvas, 1030, 915, "tealButton.fw.png", None, loadFunc)
    loadGameButton.addLabel(canvas, "LOAD\nGAME", "white", (1170, 965), 30, None, loadFunc)

    #*Labels
    maxPlayersLabel = newOptionLabel(canvas, 360, 310, "MAXIMUM\nPLAYERS:")

    stackLabel = newOptionLabel(canvas, 360, 460, "STARTING STACK:")

    gameTypeLabel = newOptionLabel(canvas, 360, 610, "GAME TYPE:")

    AILevelLabel = newOptionLabel(canvas, 360, 760, "AI LEVEL:")

    assistsLabel = newOptionLabel(canvas, 360, 910, "ASSISTS\nALLOWED:")

    window.mainloop()

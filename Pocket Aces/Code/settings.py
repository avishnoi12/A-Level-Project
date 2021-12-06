#Pocket Aces v1.1
#Date started 20/11/21
#Last Date edited 27/11/21

#?radiobuttons function

#?Need to save settings to json
#?Pop up confirmation on cancel needed
#?Sound effects needed

#!imports

import json
import os
import tkinter as tk
from tkinter.constants import HORIZONTAL
from PIL import Image, ImageTk
from functools import partial
from library import *
import titleScreen

#!subprograms
def cancel(window, event):
    buttonPressSound.play() #playing button press sound

    #loading previous and new settings
    obj = readJson("Settings.json")
    obj = obj["settings"]
    jsonString = {}
    jsonString["FullScreen"] = fullScreenButtons.get()
    jsonString["TexturePack"] = texturePackButtons.get()
    jsonString["Volume"] = SFXscale.get()
    jsonString["Tutor"] = tutorButtons.get()

    #checking if previous settings are same as new
    popUp = False
    for each in obj:
        if jsonString[each] != obj[each]:
            popUp = True

    #if changes to settings have been made
    titleScreenFunc = partial(openTitleScreen, window)
    if popUp:
        #createPopUp("\nYou have unsaved changes.", quitSettings, close) #create a pop up
        newPopUp(canvas,"Are you sure you want to leave?\nYou have unsaved changes.", titleScreenFunc, SFXscale, (700,650))
        SFXscale.place_forget() #hiding slider temporarily
    else:
        titleScreenFunc(None) #if no changes have been made

def openTitleScreen(window, event):
    #clicked 'leave' on the pop up screen
    buttonPressSound.play() #playijng button press sound
    canvas.destroy()
    #os.system('py main.py')
    titleScreen.runTitleScreen(window)
    exit()

def SFXupdate(event):
    #updating label for volume
    labelText = str(SFXscale.get()) + "%"
    canvas.itemconfigure(SFXlabel, text=labelText)

def confirm(window, event):
    #saving settings
    buttonPressSound.play()
    obj = readJson("Settings.json")
    obj["settings"]["FullScreen"] = fullScreenButtons.get()
    obj["settings"]["TexturePack"] = texturePackButtons.get()
    obj["settings"]["Volume"] = SFXscale.get()
    obj["settings"]["Tutor"] = tutorButtons.get()

    settingsFile = open("Settings.json","w")
    json.dump(obj, settingsFile, indent = 2) #writing new settings to json file
    settingsFile.close()

    #os.system('py main.py') #returning to title screen
    openTitleScreen(window, None)
    exit()

def runSettings(window):
    print("Running settings...")
    global SFXlabel, SFXscale, texturePackButtons, fullScreenButtons, tutorButtons, canvas
    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.pack()
    #!Images

    #*Creating the background image
    bgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/titleBackground.png")) #path
    bg = canvas.create_image(0, 0, image=bgImage, anchor=tk.NW)

    #*Logo
    logoImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/circleLogo.fw.png")) #path
    logo = canvas.create_image(0, 0, image=logoImage, anchor=tk.NW)

    titleImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/settingsText.fw.png"))
    screenTitle = canvas.create_image(430,130, image=titleImage, anchor=tk.NW)

    #*Radio buttons
    fullScreenButtons = newRadioButton(canvas, 700,330,["ON","OFF"],("settings"),"Settings.json",("settings","FullScreen"))

    texturePackButtons = newRadioButton(canvas, 700,480,["RED","GREEN","BLUE"],("settings"),"Settings.json",("settings","TexturePack"))

    tutorButtons = newRadioButton(canvas, 700,780,["ON","OFF"],("settings"),"Settings.json",("settings","Tutor"))

    #*SFX slider
    SFXscale = tk.Scale(canvas, from_=0, to=100, orient=HORIZONTAL, font=(FONTNAME,20), bg=TERTARYCOLOUR, activebackground="white"
        ,length=380, troughcolor=PRIMARYCOLOUR, sliderlength=20, command=SFXupdate, showvalue=0, width=20)
    SFXscale.set(getJson("Settings.json",("settings","Volume")))
    SFXscale.place(x=700,y=650)
    SFXlabel = canvas.create_text(1140,660, text=str(SFXscale.get())+"%",fill="white",font=(FONTNAME,30))

    #*Buttons
    cancelFunc = partial(cancel, window)
    cancelButton = newButton(canvas, 65, 915, "redButton.fw.png", None, cancelFunc)
    cancelButton.addLabel(canvas, "CANCEL", "white", (180,960), 30, None, cancelFunc)

    confirmFunc = partial(confirm, window)
    confirmButton = newButton(canvas, 1085, 915, "greenButton.fw.png", None, confirmFunc)
    confirmButton.addLabel(canvas, "CONFIRM", "white", (1200,960), 30, None, confirmFunc)

    #*Labels
    fullScreenLabel = newOptionLabel(canvas, 360, 310, "FULLSCREEN:")

    texturePLabel = newOptionLabel(canvas, 360, 460, "TEXTURE PACK:")

    volumeLabel = newOptionLabel(canvas, 360, 610, "SFX VOLUME:")

    tutorLabel = newOptionLabel(canvas, 360, 760, "TUTOR:")

    window.mainloop()
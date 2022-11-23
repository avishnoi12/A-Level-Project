#Pocket Aces v1.1
#Date started 27/11/21
#Last Date edited 10/12/21

#?Functions simplified
#?Creating of settings screen now inside a function

#!imports

import json
from os import name
import tkinter as tk
from tkinter.constants import HORIZONTAL
from PIL import Image, ImageTk
from functools import partial
from library import *
import titleScreen

#!subprograms
def cancel(window, event):
    global popUp, leaveButton, stayButton
    #*CANCEL button pressed
    buttonPressSound.play() #playing button press sound

    #loading previous and new settings
    obj = readJson("Settings.json")
    obj = obj["settings"]
    jsonString = {}
    jsonString["FullScreen"] = fullScreenButtons.get()
    jsonString["TexturePack"] = texturePackButtons.get()
    jsonString["Volume"] = SFXscale.get()
    jsonString["Tutor"] = tutorButtons.get()
    jsonString["Name"] = nameEntry.get()

    #checking if previous settings are same as new
    popUp = False
    for each in obj:
        if jsonString[each] != obj[each]:
            popUp = True

    if popUp: #if changes to settings have been made
        popUp = newPopUp(canvas,"Are you sure you want to leave?\nYou have unsaved changes.")

        SFXscale.place_forget() #hiding the slider from the scale

        #*Creating buttons
        titleScreenFunc = partial(openTitleScreen, window)
        leaveButton = newButton(canvas, 500, 660, "redButton.fw.png", "popUp", titleScreenFunc)
        leaveButton.addLabel(canvas, "LEAVE", "white", (615, 700), 30, "popUp", titleScreenFunc)

        stayButton = newButton(canvas, 1050, 660, "greenButton.fw.png", "popUp", closePopUp)
        stayButton.addLabel(canvas, "STAY", "white", (1165,700), 30, "popUp", closePopUp)  
    else:
        openTitleScreen(window, None) #if no changes have been made

def openTitleScreen(window, event):
    #*LEAVE button pressed on pop up
    buttonPressSound.play() #playing button press sound
    canvas.destroy()
    titleScreen.runTitleScreen(window)
    exit()

def SFXupdate(event):
    #updating label for volume
    labelText = str(SFXscale.get()) + "%"
    canvas.itemconfigure(SFXlabel, text=labelText)

def confirm(window, event):
    #*CONFIRM button pressed
    buttonPressSound.play() #playing button press sound

    #creating json string with new settings
    obj = readJson("Settings.json")
    obj["settings"]["FullScreen"] = fullScreenButtons.get()
    obj["settings"]["TexturePack"] = texturePackButtons.get()
    obj["settings"]["Volume"] = SFXscale.get()
    obj["settings"]["Tutor"] = tutorButtons.get()
    obj["settings"]["Name"] = nameEntry.get()[:10] #10 character limit

    settingsFile = open("Settings.json","w")
    json.dump(obj, settingsFile, indent = 2) #writing new settings to json file
    settingsFile.close()

    #returning to title screen
    openTitleScreen(window, None)
    exit()

def closePopUp(event):
    #*LEAVE button pressed on pop up
    buttonPressSound.play() #playing button press sound
    canvas.delete("popUp")
    SFXscale.place(x=700, y=650)

#!Main function
def runSettings(window):
    global SFXlabel, SFXscale, texturePackButtons, fullScreenButtons, tutorButtons, canvas, nameEntry
    print("Running settings...")
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

    #*Name Entry field
    nameEntry = tk.Entry(canvas, font=(FONTNAME, 30), justify=CENTER, fg="white", bg=PRIMARYCOLOUR, width=12)
    nameEntry.insert(0, getJson("Settings.json", ("settings","Name")))
    nameEntry.place(x=700,y=940)

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

    nameLabel = newOptionLabel(canvas, 360, 910, "NAME: ")

    window.mainloop()
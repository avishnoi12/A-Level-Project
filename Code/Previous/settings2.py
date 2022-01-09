#Pocket Aces v1.1
#Date started 23/11/21
#Last Date edited 27/11/21

#?settings now saved to json
#?Pop up confirmation added
#?Sound effects addded

#!imports

import json
import os
import tkinter as tk
from tkinter.constants import HORIZONTAL
from PIL import Image, ImageTk
from functools import partial
from library import *

#!subprograms
def cancel(event):
    buttonPressSound.play() #playing button press sound

    #loading previous and new settings
    obj = readJson("Settings.json")
    jsonString = newSettings()

    #checking if previous settings are same as new
    popUp = False
    for each in obj:
        if jsonString[each] != obj[each]:
            popUp = True

    #if changes to settings have been made
    if popUp:
        #createPopUp("\nYou have unsaved changes.", quitSettings, close) #create a pop up
        newPopUp("Are you sure you want to leave?\nYou have unsaved changes.", quitSettings, SFXscale, (700,650))
        SFXscale.place_forget() #hiding slider temporarily
    else:
        quitSettings(None) #if no changes have been made

def close(event):
    #clicked 'stay' on the pop up screen
    buttonPressSound.play() #playijng button press sound
    canvas.delete("popUp") #deleting pop up
    SFXscale.place(x=700,y=650) #unhiding slider

def quitSettings(event):
    #clicked 'leave' on the pop up screen
    buttonPressSound.play() #playijng button press sound
    os.system('py main.py')
    exit()

def SFXupdate(event):
    #updating label for volume
    labelText = str(SFXscale.get()) + "%"
    canvas.itemconfigure(SFXlabel, text=labelText)

def confirm(event):
    #saving settings
    buttonPressSound.play()
    jsonString = newSettings() #creating dictionary of all selected settings

    settingsFile = open("Settings.json","w")
    json.dump(jsonString, settingsFile, indent = 2) #writing new settings to json file
    settingsFile.close()

    os.system('py main.py') #returning to title screen
    exit()

def newSettings():
    #creating dictionary of all selected settings
    jsonString = {}
    jsonString["ScreenRes"] = screenResButtons.get()
    jsonString["TexturePack"] = texturePackButtons.get()
    jsonString["Volume"] = SFXscale.get()
    jsonString["Tutor"] = tutorButtons.get()
    jsonString["BgMusic"] = True
    return jsonString

#*Creating the window
#window = tk.Tk()
window.geometry("1920x1080")
window.attributes("-fullscreen", True) #setting to fullscreenn
window.title("Pocket Aces")
print("Running settings...")

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
screenResButtons = newRadioButton(canvas, 700,330,["1080p","720p","480p"],("settings"),"ScreenRes")

texturePackButtons = newRadioButton(canvas, 700,480,["RED","GREEN","BLUE"],("settings"),"TexturePack")

tutorButtons = newRadioButton(canvas, 700,780,["ON","OFF"],("settings"),"Tutor")

#*SFX slider
SFXscale = tk.Scale(canvas, from_=0, to=100, orient=HORIZONTAL, font=(FONTNAME,20), bg=TERTARYCOLOUR, activebackground="white"
    ,length=380, troughcolor=PRIMARYCOLOUR, sliderlength=20, command=SFXupdate, showvalue=0, width=20)
SFXscale.set(getJson("Settings.json","Volume"))
SFXscale.place(x=700,y=650)
SFXlabel = canvas.create_text(1140,660, text=str(SFXscale.get())+"%",fill="white",font=(FONTNAME,30))

#*Buttons
cancelButton = newButton(canvas, 65, 915, "cancel.fw.png", None, cancel)

confirmButton = newButton(canvas, 1085, 915, "confirm.fw.png", None, confirm)

#*Labels
screenResLabel = newOptionLabel(canvas, 360, 310, "SCREEN\n RESOLUTION:")

texturePLabel = newOptionLabel(canvas, 360, 460, "TEXTURE PACK:")

volumeLabel = newOptionLabel(canvas, 360, 610, "SFX VOLUME:")

tutorLabel = newOptionLabel(canvas, 360, 760, "TUTOR:")

window.mainloop()
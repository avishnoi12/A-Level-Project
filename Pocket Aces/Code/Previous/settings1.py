#Pocket Aces v1.1
#Date started 20/11/21
#Last Date edited 23/11/21

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

#!subprograms
def cancel(event): #TODO Pop-up confimation
    os.system('py main.py')
    exit()

def SFXupdate(event):
    labelText = str(SFXscale.get()) + "%"
    canvas.itemconfigure(SFXlabel, text=labelText)

def confirm(event): #TODO Save settings to JSON and live update settings
    print(screenResButtons.get())
    print(texturePackButtons.get())
    print(SFXscale.get())
    print(tutorButtons.get())


#*Creating the window
#window = tk.Tk()
window.geometry("1920x1080")
window.attributes("-fullscreen", True) #setting to fullscreenn
window.title("Pocket Aces")

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
screenResButtons = newRadioButton(canvas, 700,330,["1080p","720p","480p"],0)

texturePackButtons = newRadioButton(canvas, 700,480,["RED","GREEN","BLUE"],1)

tutorButtons = newRadioButton(canvas, 700,780,["ON","OFF"],0)

#*SFX slider
SFXscale = tk.Scale(canvas, from_=0, to=100, orient=HORIZONTAL, font=(FONTNAME,20), bg=TERTARYCOLOUR, activebackground="white"
    ,length=380, troughcolor=PRIMARYCOLOUR, sliderlength=20, command=SFXupdate, showvalue=0, width=20)
SFXscale.set(100)
SFXscale.place(x=700,y=650)
SFXlabel = canvas.create_text(1140,660, text=str(SFXscale.get())+"%",fill="white",font=(FONTNAME,30))

#*Buttons
cancelButton = newButton(canvas, 65, 915, "cancel.fw.png", cancel)

confirmButton = newButton(canvas, 1085, 915, "confirm.fw.png", confirm)

#*Labels
screenResLabel = newOptionLabel(canvas, 360, 310, "      SCREEN\n RESOLUTION:")

texturePLabel = newOptionLabel(canvas, 360, 460, "TEXTURE PACK:")

volumeLabel = newOptionLabel(canvas, 360, 610, "SFX VOLUME:")

tutorLabel = newOptionLabel(canvas, 360, 760, "TUTOR:")

window.mainloop()
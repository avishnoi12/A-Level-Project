#Pocket Aces v1.1
#Date started 18/11/21
#Last Date edited 22/11/21

#?Majority of button functions not implemented
#?Title screen UI complete
#?Sound effects needed

#? Radiobuttons class added

#!imports

import threading
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

#!constants

FONTNAME = "Berlin Sans FB"
PRIMARYCOLOUR = "#11AD70"
SECONDARYCOLOUR = "#13D186"
TERTARYCOLOUR = "#0E8D5A"


#!classes

class newButton(object):
    def __init__(self,canvas,xCoOrd,yCoOrd,imgPath,func):
        self.coOrds = (xCoOrd, yCoOrd) #tuple of co-ordinates
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        self.button = canvas.create_image(xCoOrd,yCoOrd,image=self.physImage, anchor=tk.NW)
        canvas.tag_bind(self.button, "<Button-1>", func) #making the image a button

    def addLabel(self, canvas, label, colour, centre, size, func):
        self.buttonLabel = canvas.create_text(centre[0],centre[1],text=label, font=(FONTNAME,size), fill=colour)
        canvas.tag_bind(self.buttonLabel, "<Button-1>", func) #making the text a button
        #users will be able to click anywhere on the button (including text) to call the button's function

    def changeImage(self, canvas, imgPath):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        canvas.itemconfigure(self.button, image=self.physImage)

class newRadioButton(newButton):
    def __init__(self, canvas, xCoOrd, yCoOrd, options, default):
        self.buttons = [] #array of all button objects
        self.options = options
        self.value = tk.IntVar() #index of selected option
        self.value.set(default)

        #creating buttonobject for each option
        for index, each in enumerate(options): 
            if index == self.value.get(): #choosing which image to use
                imgPath = "selected.fw.png"
            else:
                imgPath = "option.fw.png"

            func = partial(self.clicked, canvas, index) #function to be called when clicked
            #creating button and adding label to it
            self.buttons.append(newButton(canvas, xCoOrd, yCoOrd, imgPath, func))
            self.buttons[-1].addLabel(canvas, each, "white", (xCoOrd+62,yCoOrd+30), 20, func) 
            xCoOrd += 130 #the next button placed 130 pixels along from previous
    
    def clicked(self, canvas, index, event):
        if self.value.get() != index: #radio button clicked was previously not selected
            #swapping images of clicked and selected button
            self.buttons[index].changeImage(canvas, "selected.fw.png")
            self.buttons[self.value.get()].changeImage(canvas, "option.fw.png")
            self.value.set(index) #changing index to new value

    def get(self): #returns the option selected from radio
        return self.options[self.value.get()]

class newOptionLabel(object):
    def __init__(self, canvas, xCoOrd, yCoOrd, textLabel):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/optionLabel.fw.png"))
        self.label = canvas.create_image(xCoOrd,yCoOrd,image=self.physImage, anchor=tk.NW)
        self.text = canvas.create_text(xCoOrd+150, yCoOrd+50, text=textLabel, font=(FONTNAME,20), fill="white")


#!subprograms

def quitGame(event):
    #TODO function should open pop-up asking user if they would like to quit
    window.destroy()
    exit()

def runSettings(event):
    os.system('python settings1.py')
    exit()

#!main program


if __name__ == '__main__':
    #*Creating the window
    window = tk.Tk()
    window.geometry("1920x1080")
    window.attributes("-fullscreen", True) #setting to fullscreenn
    window.title("Pocket Aces")

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
    quitButton = newButton(canvas, 855,795,"TitleScreen/optionButton.fw.png",quitGame)
    quitButton.addLabel(canvas, "QUIT","white",(1085,865),30,quitGame)

    #*Settings button
    settingsButton = newButton(canvas, 954,295,"TitleScreen/optionButton.fw.png",runSettings) #TODO function should lead to settings screen
    settingsButton.addLabel(canvas, "SETTINGS","white",(1184,365),30,runSettings)

    #*Tutorials button
    tutorialsButton = newButton(canvas, 905,545,"TitleScreen/optionButton.fw.png",None) #TODO function should lead to tutorials screen
    tutorialsButton.addLabel(canvas, "TUTORIALS","white",(1135,615),30,None)

    #*Play button
    playButton = newButton(canvas, 285,735,"TitleScreen/playButton.fw.png",None) #TODO function should lead to gameplay screen
    playButton.addLabel(canvas, "PLAY NOW",SECONDARYCOLOUR,(515,805),30,None)

    window.mainloop()

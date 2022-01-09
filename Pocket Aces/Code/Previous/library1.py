#Pocket Aces Library
#Date started 23/11/21
#Last edited 25/11/21

#?Button classes finished
#?Json subrpograms needed
#?classes for labels neded

#!Imports

import threading
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

#!Constants

window = tk.Tk()
canvas = tk.Canvas(window, width=1920, height=1080)
canvas.pack()

FONTNAME = "Berlin Sans FB"
PRIMARYCOLOUR = "#11AD70"
SECONDARYCOLOUR = "#13D186"
TERTARYCOLOUR = "#0E8D5A"

#!Classes

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

class newRadioButton(object):
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

#Subprograms

def quitGame(event):
    #TODO function should open pop-up asking user if they would like to quit
    exit()

def runSettings(event):
    os.system('py settings.py')
    exit()
#Pocket Aces Library
#Date started 23/11/21
#Last edited 23/11/21

#!Imports

from tkinter.constants import CENTER
import pygame
import json
import threading
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

#!Constants

FONTNAME = "Berlin Sans FB"
PRIMARYCOLOUR = "#11AD70"
SECONDARYCOLOUR = "#13D186"
TERTARYCOLOUR = "#0E8D5A"

pygame.mixer.init()
buttonPressSound = pygame.mixer.Sound("../Entities/SFX/buttonPress.wav")
buttonPressSound.set_volume(0.3)

#!Classes

class newButton(object):
    def __init__(self,canvas,xCoOrd,yCoOrd,imgPath,allTags,func):
        self.coOrds = (xCoOrd, yCoOrd) #tuple of co-ordinates
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        self.button = canvas.create_image(xCoOrd,yCoOrd,image=self.physImage, anchor=tk.NW, tags=allTags)
        canvas.tag_bind(self.button, "<Button-1>", func) #making the image a button

    def addLabel(self, canvas, label, colour, centre, size, allTags, func):
        self.buttonLabel = canvas.create_text(centre[0],centre[1],text=label, font=(FONTNAME,size), fill=colour, tags=allTags, justify=CENTER)
        canvas.tag_bind(self.buttonLabel, "<Button-1>", func) #making the text a button
        #users will be able to click anywhere on the button (including text) to call the button's function

    def changeImage(self, canvas, imgPath):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        canvas.itemconfigure(self.button, image=self.physImage)

class newRadioButton(object):
    def __init__(self, canvas, xCoOrd, yCoOrd, options, allTags, filename, keys):
        self.buttons = [] #array of all button objects
        self.options = options
        self.value = tk.IntVar() #index of selected option
        self.setDefault(filename, keys)

        #creating buttonobject for each option
        for index, each in enumerate(options): 
            if index == self.value.get(): #choosing which image to use
                imgPath = "selected.fw.png"
            else:
                imgPath = "option.fw.png"

            func = partial(self.clicked, canvas, index) #function to be called when clicked
            #creating button and adding label to it
            self.buttons.append(newButton(canvas, xCoOrd, yCoOrd, imgPath, allTags, func))
            self.buttons[-1].addLabel(canvas, each, "white", (xCoOrd+62,yCoOrd+30), 20, allTags, func) 
            xCoOrd += 130 #the next button placed 130 pixels along from previous
    
    def clicked(self, canvas, index, event):
        if self.value.get() != index: #radio button clicked was previously not selected
            #swapping images of clicked and selected button
            self.buttons[index].changeImage(canvas, "selected.fw.png")
            self.buttons[self.value.get()].changeImage(canvas, "option.fw.png")
            self.value.set(index) #changing index to new value
            buttonPressSound.play() #play button sound

    def get(self): #returns the option selected from radio
        return self.options[self.value.get()]

    def setDefault(self, filename, keys):
        newValue = getJson(filename, keys)
        self.value.set(self.options.index(newValue)) #setting default value

    def greyOrUngrey(self, canvas, grey):
        for index, each in enumerate(self.buttons): 
            if index == self.value.get(): #choosing which image to use
                imgPath = "selected.fw.png"
            else:
                imgPath = "option.fw.png"
            
            if grey:
                each.changeImage(canvas, "g_"+imgPath)
                canvas.tag_unbind(each.button)
            else:
                func = partial(self.clicked, canvas, index) #function to be called when clicked
                each.changeImage(canvas, imgPath)
                canvas.tag_bind(each.button, "<Button-1>", func)

class newOptionLabel(object):
    def __init__(self, canvas, xCoOrd, yCoOrd, textLabel):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/optionLabel.fw.png"))
        self.label = canvas.create_image(xCoOrd,yCoOrd,image=self.physImage, anchor=tk.NW)
        self.text = canvas.create_text(xCoOrd+150, yCoOrd+50, text=textLabel, font=(FONTNAME,20), fill="white", justify = CENTER)

    def hover(self, canvas, xCoOrd, yCoOrd, helpText):
        self.helpLabel = canvas.create_text(xCoOrd,yCoOrd,text=helpText, font=(FONTNAME,20), fill="white", justify = CENTER)

class newPopUp(object):
    def __init__(self, canvas, allText, func, scale, coOrds):
        self.physImage = popUpImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/popUpNew.fw.png"))
        self.popUpLabel = canvas.create_image(400, 400, image=popUpImage, anchor=tk.NW, tags="popUp")
        self.text = canvas.create_text(875, 500, text=allText, font = (FONTNAME,40), fill = "white", tags="popUp", justify=CENTER)

        if scale is not None:
            closeFunc = partial(self.closePopUp, canvas, scale, coOrds)
        else:
            closeFunc = partial(self.closePopUp, canvas, None, None)

        if func is None: #pop up requires single button (to close it)
            closeText = "OK"
        else:
            self.leaveButton = newButton(canvas, 500, 660, "redButton.fw.png", "popUp", func)
            self.leaveButton.addLabel(canvas, "LEAVE", "white", (615,700), 30, "popUp", func)
            closeText = "STAY"
        self.closeButton = newButton(canvas, 1050, 660, "greenButton.fw.png", "popUp", closeFunc)
        self.closeButton.addLabel(canvas, closeText, "white", (1165,700), 30, "popUp", closeFunc)
    
    def closePopUp(self, canvas, scale, coOrds, event):
        buttonPressSound.play()
        canvas.delete("popUp")
        if scale is not None:
            scale.place(x=coOrds[0], y=coOrds[1])

#Subprograms

def readJson(filename):
    #reading the json file
    jsonFile = open(filename,"r")
    obj = json.loads(jsonFile.read())
    return obj

def getJson(filename, keys):
    #opening the settings json
    obj = readJson(filename)
    temp = obj
    for key in keys:
        temp = temp[key] #storing requred data
    return temp

def setJson(filename, keys, value):
    obj = readJson(filename)
    temp = obj
    for key in (keys):
        temp = temp[key]
    temp = value
    jsonFile = open(filename, "w")
    json.dump(obj, jsonFile, indent = 2) #writing new settings to json file
    jsonFile.close()
    
def exitGame(event):
    buttonPressSound.play()
    setJson("Settings.json",("options","Running"),False)
    time.sleep(0.25)
    print("Quitting game...")
    exit()

#background music
bgMusic = pygame.mixer.music.load("../Entities/SFX/bgMusic.mp3")
pygame.mixer.music.play(-1)
setJson("Settings.json", ("options","Running"), True)
settingsVolume = (getJson("Settings.json",("settings","Volume")))/100
pygame.mixer.music.set_volume(round(settingsVolume,2))
buttonPressSound.set_volume(round(settingsVolume,2))
print("Opened library...")

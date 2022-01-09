#Pocket Aces Library
#Date started 28/11/21
#Last edited 24/12/21

#?added pygame music
#?Added help feature to optionLabel

#!Imports

from tkinter.constants import CENTER, E
import pygame
import json
import time
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

from pygame.constants import CONTROLLER_BUTTON_LEFTSTICK

#!Constants

FONTNAME = "Berlin Sans FB"
BOLDFONT = "Berlin Sans FB Demi"
PRIMARYCOLOUR = "#11AD70"
SECONDARYCOLOUR = "#13D186"
TERTARYCOLOUR = "#0E8D5A"

#!Classes

class newButton(object):
    def __init__(self,canvas,xCoOrd,yCoOrd,imgPath,allTags,func):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        self.coOrds = (xCoOrd, yCoOrd)
        self.allTags = allTags
        self.func = func
        self.place(canvas)

    def place(self, canvas): #places the button
        self.button = canvas.create_image(self.coOrds,image=self.physImage, anchor=tk.NW, tags=self.allTags)
        self.binded = canvas.tag_bind(self.button, "<Button-1>", self.func) #making the image a button

    def unplace(self, canvas):
        canvas.delete(self.button)

    def addLabel(self, canvas, label, colour, centre, size, allTags, func):
        self.buttonLabel = canvas.create_text(centre,text=label, font=(FONTNAME,size), fill=colour, tags=allTags, justify=CENTER)
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

class preSelectButtons(object):
    def __init__(self, canvas):
        self.buttons = []
        self.value = tk.IntVar()
        self.value.set(5) #5 represents no button selected
        self.folder = "PreSelect/"
        self.imgPaths = ["callAny.fw.png","call.fw.png","check.fw.png","fold.fw.png"]
        #co ordinates of buttons
        yCoOrd = 930
        xCoOrds = [60,370,1300,1610]

        #*placing buttons
        for index, img in enumerate(self.imgPaths):
            func = partial(self.clicked, canvas, index)
            self.buttons.append(newButton(canvas, xCoOrds[index], yCoOrd, self.folder+img, "preSelect", func))

    def clicked(self, canvas, index, event):
        if self.value.get() == 5: #no button selected
            self.buttons[index].changeImage(canvas, self.folder+"t_"+self.imgPaths[index]) #change image to true
            self.value.set(index)
        elif self.value.get() != index: #radio button clicked was previously not selected
            self.buttons[index].changeImage(canvas, self.folder+"t_"+self.imgPaths[index]) #change image to true
            self.buttons[self.value.get()].changeImage(canvas, self.folder+self.imgPaths[self.value.get()]) #change image to false
            self.value.set(index)
        elif self.value.get() == index: #radio button clicked was selected previously
            self.buttons[index].changeImage(canvas, self.folder+self.imgPaths[index])
            self.value.set(5) #represents no button selected

    def get(self): #returns the index of the option selected
        return self.value.get()

    def hide(self, canvas): #hides all buttons
        for btn in self.buttons:
            btn.unplace(canvas)

    def place(self, canvas): #replaces all buttons
        for btn in self.buttons:
            btn.place(canvas)

    def disable(self, canvas, index): #disables a single button (grey)
        btn = self.buttons[index]

        #*validation
        try: #only some buttons can be disabled
            canvas.tag_unbind(btn.button, "<Button-1>", btn.binded)
        except: #button cannot be disabled
            pass
        else: #can be disabled
            btn.changeImage(canvas, self.folder+"g_"+self.imgPaths[index]) #changing image
            
    def enable(self, canvas, index): #enables a single button
        btn = self.buttons[index]
        btn.changeImage(canvas, self.folder+self.imgPaths[index])
        btn.binded = canvas.tag_bind(btn.button, "<Button-1>", btn.func)

    def deselect(self, canvas): #deselects current button
        index = self.value.get()
        #*validation
        try:
            self.buttons[index].changeImage(canvas, self.folder+self.imgPaths[index])
        except:
            print("No button was selected")
        else:
            self.value.set(5) #represents no button selected
        
class newOptionLabel(object):
    def __init__(self, canvas, xCoOrd, yCoOrd, textLabel):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/optionLabel.fw.png"))
        self.label = canvas.create_image(xCoOrd,yCoOrd,image=self.physImage, anchor=tk.NW)
        self.text = canvas.create_text(xCoOrd+150, yCoOrd+50, text=textLabel, font=(FONTNAME,20), fill="white", justify = CENTER)

    def hover(self, canvas, xCoOrd, yCoOrd, helpText):
        self.helpLabel = canvas.create_text(xCoOrd,yCoOrd,text=helpText, font=(FONTNAME,20), fill="white", justify = CENTER)

class newPopUp(object):
    def __init__(self, canvas, allText):
        self.physImage = popUpImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/popUpNew.fw.png"))
        self.popUpLabel = canvas.create_image(400, 400, image=popUpImage, anchor=tk.NW, tags="popUp")
        self.text = canvas.create_text(875, 500, text=allText, font = (FONTNAME,40), fill = "white", tags="popUp", justify=CENTER)

#Subprograms

def readJson(filename):
    #turns json file into python dictionary
    jsonFile = open(filename,"r")
    obj = json.loads(jsonFile.read())
    return obj

def getJson(filename, keys):
    #gets specific value from json file
    obj = readJson(filename)
    temp = obj
    for key in keys: #finding required value
        temp = temp[key] #storing requred data
    return temp

def setJson(filename, keys, value):
    #sets specific value in json file to new value
    obj = readJson(filename)
    temp = obj
    for key in (keys): #finding required value
        temp = temp[key]
    temp = value
    jsonFile = open(filename, "w")
    json.dump(obj, jsonFile, indent = 2) #writing new settings to json file
    jsonFile.close()
    
def exitGame(event):
    buttonPressSound.play()
    time.sleep(0.25)
    print("Quitting game...")
    exit()

#!music and sfx
pygame.mixer.init() #initialises music feature
settingsVolume = (getJson("Settings.json",("settings","Volume")))/100 #gets volume from json file

#*Button press sound effect
buttonPressSound = pygame.mixer.Sound("../Entities/SFX/buttonPress.wav")
buttonPressSound.set_volume(round(settingsVolume,2)) #sets the volume to the value from json file

#*background music
bgMusic = pygame.mixer.music.load("../Entities/SFX/bgMusic.mp3")
pygame.mixer.music.play(-1) #loops music
pygame.mixer.music.set_volume(round(settingsVolume,2)) #sets the volume to the value from json file

print("Opened library...")

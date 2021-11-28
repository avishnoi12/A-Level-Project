#Pocket Aces v1.1
#Date started 17/11/21
#Last Date edited 18/11/21

#?Majority of button functions not implemented
#?Title screen UI complete

#!imports

import tkinter as tk
from PIL import Image, ImageTk

#!constants

FONTNAME = ("Berlin Sans FB",30)
PRIMARYCOLOUR = "#11AD70"
SECONDARYCOLOUR = "#13D186"
TERTARYCOLOUR = "#0E8D5A"


#!classes

class newButton(object):
    def __init__(self,xCoOrd,yCoOrd,imgPath,func):
        self.coOrds = (xCoOrd, yCoOrd) #tuple of co-ordinates
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        self.button = canvas.create_image(xCoOrd,yCoOrd,image=self.physImage, anchor=tk.NW)
        canvas.tag_bind(self.button, "<Button-1>", func) #making the image a button

    def addLabel(self, label, colour, func): #TODO correct centre co-ords so they align correctly for any image
        x = self.coOrds[0]+230
        y = self.coOrds[1]+70
        self.centre = (x,y) #tuple of centre co-ordinates
        self.buttonLabel = canvas.create_text(x,y,text=label, font=FONTNAME, fill=colour)
        canvas.tag_bind(self.buttonLabel, "<Button-1>", func) #making the text a button
        #users will be able to click anywhere on the button (including text) to call the button's function

    def changeImage(self, imgPath):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        canvas.itemconfigure(self.button, image=self.physImage)

#!subprograms

def quitGame(event):
    #TODO function should open pop-up asking user if they would like to quit 
    window.destroy()

#!main program

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
quitButton = newButton(855,795,"TitleScreen/optionButton.fw.png",quitGame)
quitButton.addLabel("QUIT","white",quitGame)

#*Settings button
settingsButton = newButton(954,295,"TitleScreen/optionButton.fw.png",None) #TODO function should lead to settings screen
settingsButton.addLabel("SETTINGS","white",None)

#*Tutorials button
tutorialsButton = newButton(905,545,"TitleScreen/optionButton.fw.png",None) #TODO function should lead to tutorials screen
tutorialsButton.addLabel("TUTORIALS","white",None)

#*Play button
playButton = newButton(285,735,"TitleScreen/playButton.fw.png",None) #TODO function should lead to gameplay screen
playButton.addLabel("PLAY NOW",SECONDARYCOLOUR,None)

window.mainloop()

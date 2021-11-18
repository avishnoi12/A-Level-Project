#Pocket Aces v1.0
#Date started 10/11/21
#Last Date edited 17/11/21

#?Uncompleted title screen - need to add playblock and imagery
#?Majority of button functions not implemented

#!imports

import tkinter as tk
from PIL import Image, ImageTk

#!constants


#!classes

class newButton(object):
    def __init__(self,imgPath,func):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath))
        self.button = tk.Label(canvas, image=self.physImage, bd=0)
        self.button.bind("<Button-1>",func) #making the label a button

    def place(self,xCoOrd,yCoOrd):
        self.button.place(x=xCoOrd,y=yCoOrd) #placing the label onto the canvas

    def changeimage(self, imgPath):
        self.physImage = ImageTk.PhotoImage(Image.open("../Entities/Buttons/"+imgPath)) #new image
        self.button.configure(image=self.physImage) #changing image of label to new image
        self.button.image = self.physImage

#!subprograms

def quitGame(event): #TODO function should open pop-up asking user if they would like to quit 
    window.destroy()

#!main program

#*creating the window
window = tk.Tk()
window.geometry("1920x1080")
#window.attributes("-fullscreen", True) #setting to fullscreenn
window.title("Pocket Aces")
window.lift() #bringing window infront of all other windows

canvas = tk.Canvas(window, bg="black", width=1920, height=1080)
canvas.pack()

#*creating the background image
bgImage = ImageTk.PhotoImage(file="../Entities/Background/titleBackground.png") #path
bg = canvas.create_image(0, 0, image=bgImage, anchor=tk.NW)

#*logo
logoImage = ImageTk.PhotoImage(file="../Entities/Icons/Logo.png") #path
logo = canvas.create_image(0, 0, image=logoImage, anchor=tk.NW)

#*Quit button
quitButton = newButton("TitleScreen/quit.fw.png", quitGame)
quitButton.place(855,795)

#*Settings button
settingsButton = newButton("TitleScreen/settings.fw.png", None) #TODO function should lead to settings screen
settingsButton.place(954,295)

#*Tutorials button
tutorialsButton = newButton("TitleScreen/tutorials.fw.png", None) #TODO function should lead to tutorials screen
tutorialsButton.place(905,545)

#*Play button
playButton = newButton("TitleScreen/playButton.fw.png", None) #TODO function should lead to gameplay screen
playButton.place(290,730)

#?testing
radio = tk.Radiobutton(canvas)

window.mainloop()

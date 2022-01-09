#Pocket Aces v1.1
#Date started 22/11/21
#Last Date edited 01/12/21

#?Majority of button functions not implemented
#?Sound effects needed

#?Funtions and classes moved to library.py

#!imports

import pygame
from library import *
import threading
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

#!main program

#*Creating the window
#window = tk.Tk()
window.geometry("1920x1080")
window.attributes("-fullscreen", True) #setting to fullscreen
window.title("Pocket Aces")
print("Running main...")

#music and sounds
if not getJson("Settings.json","BgMusic"):
    bgMusic = pygame.mixer.music.load("../Entities/SFX/bgMusic.mp3")
    pygame.mixer.music.set_volume((getJson("Settings.json","Volume"))/100)
    pygame.mixer.music.play(-1)
    setJson("Settings.json", "BgMusic", True)

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
quitButton = newButton(canvas, 855,795,"TitleScreen/optionButton.fw.png",("title"),quitGame)
quitButton.addLabel(canvas, "QUIT","white",(1085,865),30,("title"),quitGame)

#*Settings button
settingsButton = newButton(canvas, 954,295,"TitleScreen/optionButton.fw.png",("title"),runSettings) #TODO function should lead to settings screen
settingsButton.addLabel(canvas, "SETTINGS","white",(1184,365),30,("title"),runSettings)

#*Tutorials button
tutorialsButton = newButton(canvas, 905,545,"TitleScreen/optionButton.fw.png",("title"),None) #TODO function should lead to tutorials screen
tutorialsButton.addLabel(canvas, "TUTORIALS","white",(1135,615),30,("title"),None)

#*Play button
playButton = newButton(canvas, 285,735,"TitleScreen/playButton.fw.png",("title"),None) #TODO function should lead to gameplay screen
playButton.addLabel(canvas, "PLAY NOW",SECONDARYCOLOUR,(515,805),30,("title"),None)

window.mainloop()

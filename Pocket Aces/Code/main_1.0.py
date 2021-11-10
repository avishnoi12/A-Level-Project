#Pocket Aces v1.0
#Date started 10/11/21
#Last Date edited 10/11/21

#imports
import tkinter as tk

#constants

#subprograms

#%main program

#!creating the window
window = tk.Tk()
window.attributes("-fullscreen", True) #setting to fullscreenn
window.title("Pocket Aces")

#!creating the background image
bgImage = tk.PhotoImage(file="../Entities/Background/titleBackground.png") #path
background = tk.Label(window, image = bgImage)
background.place(x=0, y=0)

#!logo
logoImage = tk.PhotoImage(file="../Entities/Icons/Logo.png") #path
logo = tk.Label(window, image = logoImage).place(x=0, y=0)

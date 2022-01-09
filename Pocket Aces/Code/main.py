#Pocket Aces v1.1
#Date started 01/12/21
#Last Date edited 10/12/21

#?Title screen moved to new file

#!imports
from library import *
import titleScreen
import tkinter as tk

#!main program
#*Creating the window
window = tk.Tk()
window.geometry("1920x1080")
window.title("Pocket Aces")
print("Running main...")

#*Creating title screen
titleScreen.runTitleScreen(window)

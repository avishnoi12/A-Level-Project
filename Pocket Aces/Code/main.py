#Pocket Aces v1.1
#Date started 17/11/21
#Last Date edited 23/11/21

#?Majority of button functions not implemented
#?Sound effects needed

#?Funtions moved to library.py

#!imports

import pygame
from library import *
import titleScreen
import threading
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

#!subprograms

#!main program

#*Creating the window
window = tk.Tk()
window.geometry("1920x1080")
#window.attributes("-fullscreen", True) #setting to fullscreen
window.title("Pocket Aces")
print("Running main...")

titleScreen.runTitleScreen(window)

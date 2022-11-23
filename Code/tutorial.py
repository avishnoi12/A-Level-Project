#Pocket Aces tutorials
#Date started 10/12/21
#Last edited 10/12/21

#?Pop up screen - feature not available in thie current prototype

#! imports
from library import *
import titleScreen
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial
import webbrowser

allHelp = ["How to Play", "Tutor Help", "Controls"]
screenIndex = 0

def openTitleScreen(window, event):
    buttonPressSound.play()
    canvas.destroy()
    titleScreen.runTitleScreen(window)
    exit()

def nextHelp(event):
    global screenIndex, prevHelpBtn
    screenIndex += 1

    #*Previous button and label
    prevHelpBtn = newButton(canvas, 400, 915, "redButton.fw.png", "previous", prevHelp)
    prevHelpBtn.addLabel(canvas, "PREVIOUS", "white", (510, 960), 30, "previous", prevHelp)
    canvas.itemconfigure(prevHelpLabel, text=allHelp[screenIndex-1]) #updating label
    
    if screenIndex == 2: #len(allHelp) - 1
        canvas.delete("continue")
        canvas.itemconfigure(nextHelpLabel, text="")
    else:
        canvas.itemconfigure(nextHelpLabel, text=allHelp[screenIndex+1]) #updating label

    displayHelp()

def prevHelp(event):
    global screenIndex, continueBtn
    screenIndex -= 1

    #*Continue button and label
    continueBtn = newButton(canvas, 1110, 915, "greenButton.fw.png", "continue", nextHelp)
    continueBtn.addLabel(canvas, "CONTINUE", "white", (1220, 960), 30, "continue", nextHelp)
    canvas.itemconfigure(nextHelpLabel, text=allHelp[screenIndex+1]) #updating label
    
    if screenIndex == 0:
        canvas.delete("previous")
        canvas.itemconfigure(prevHelpLabel, text="")
    else:
        canvas.itemconfigure(prevHelpLabel, text=allHelp[screenIndex-1]) #updating label

    displayHelp()

def displayHelp():
    global loadVidBtn, rankImage, actionsImage, tutorImage, preSelectExample, actionExample
    global checkIconImg, raiseIconImg, foldIconImg, callIconImg, allInIconImg, raiseImage, onTurnImage

    screen = allHelp[screenIndex]
    canvas.delete("help")
    if screen == "How to Play":
        rankImage = ImageTk.PhotoImage(Image.open("../Entities/Tutorials/rankImage.png"))
        helpImage = canvas.create_image(375, 50, image=rankImage, anchor = tk.NW, tags="help")

        actionsImage = ImageTk.PhotoImage(Image.open("../Entities/Tutorials/bettingActions.png"))
        bettingHelp = canvas.create_image(1100, 50, image=actionsImage, anchor = tk.NW, tags="help")

        loadVidBtn = newButton(canvas, 1450, 915, "greenButton.fw.png", "help", loadVideo)
        loadVidBtn.addLabel(canvas, "VIDEO", "white", (1570, 960), 30, "help", loadVideo)
    elif screen == "Tutor Help":
        tutorHelpText = "The Poker Tutor gives you various poker statistics\nas well as suggests tips and moves!\n\nStatisitcs:"
        tutorHelpText+= "\nExpected Value (EV) is the expected amount to win if you call.\nGenerally positive EV means a good move!"
        tutorHelpText+= "\n\nOuts are cards that improve your rank.\nA higher number of outs means a higher chance of improving"
        tutorHelpText+= "\n\nEquity is an APPROXIMATE win percentage.\nIt is based off of how likely you are to 'hit' one of your outs!\nThe Tutors mouth also displays Equity"
        tutorHelpText+= "\n\nPot Odds is simply the ratio of the amount to call and the amount in the pot\nHigher pot odds means more bang for your buck!"
        tutorHelpText += "\n\nThe probabilities of each rank are also displayed by the Poker Tutor"
        tutorHelpText+= "\n\nThe Poker Tutor also displays your best rank"
        tutorHelpText += "\n\nLastly, the Poker Tutor will ocassionally suggest moves! So keep an eye out for when it speaks"

        canvas.create_text(150, 150, text=tutorHelpText, font=(FONTNAME, 22), fill="white", tags="help", anchor=tk.NW, justify=CENTER)

        #tutorHelpText = "How to use the Tutor: Click the 'expand' arrow to get all your statistics!\n\nClick the 'refresh' icon to refresh your statistics\n\nOnce you're done, click the 'collapse' arrow to hide the statistics"

        tutorImage = ImageTk.PhotoImage(Image.open("../Entities/Tutorials/tutorHelp.png"))
        helpImage = canvas.create_image(1300, 30, image=tutorImage, anchor = tk.NW, tags="help")
    elif screen == "Controls": 
        preSelectExample = newButton(canvas, 400, 50, "/PreSelect/call.fw.png", "help", None)
        canvas.create_text(670, 30, text="Preselect buttons\nare parallelogram\nshaped buttons\nthat allow you to\nselect a move before your go",
            font=(FONTNAME, 22), fill="white", tags="help", anchor=tk.NW, justify=CENTER)

        actionExample = newButton(canvas, 400, 250, "/Action/call.fw.png", "help", None)
        canvas.create_text(690, 270, text="Normal action buttons are\nrounded rectangles.",
            font=(FONTNAME, 22), fill="white", tags="help", anchor=tk.NW, justify=CENTER)

        canvas.create_text(50, 445, text="Player moves are represented by\nan icon and sometimes a cash amount\nThe types of icons are shown",
            font=(FONTNAME, 22), fill="white", tags="help", anchor=tk.NW, justify=CENTER)
        canvas.create_text(240, 560, text="CHECK\n\nFOLD\n\nCALL\n\nRAISE\n\nALL IN",
            font=(FONTNAME, 24), fill="white", tags="help", anchor=tk.NW, justify=CENTER)

        checkIconImg = ImageTk.PhotoImage(Image.open("../Entities/Icons/Action/check.png"))
        foldIconImg = ImageTk.PhotoImage(Image.open("../Entities/Icons/Action/fold.png"))
        callIconImg = ImageTk.PhotoImage(Image.open("../Entities/Icons/Action/call.png"))
        raiseIconImg = ImageTk.PhotoImage(Image.open("../Entities/Icons/Action/raise.png"))
        allInIconImg = ImageTk.PhotoImage(Image.open("../Entities/Icons/Action/allIn.fw.png"))

        canvas.create_image(150, 550, image=checkIconImg, anchor = tk.NW, tags="help")
        canvas.create_image(150, 620, image=foldIconImg, anchor = tk.NW, tags="help")
        canvas.create_image(150, 690, image=callIconImg, anchor = tk.NW, tags="help")
        canvas.create_image(150, 760, image=raiseIconImg, anchor = tk.NW, tags="help")
        canvas.create_image(150, 830, image=allInIconImg, anchor = tk.NW, tags="help")

        raiseImage = ImageTk.PhotoImage(Image.open("../Entities/Tutorials/raise.png"))
        canvas.create_image(1200, 50, image=raiseImage, anchor=tk.NW, tags="help")
        canvas.create_text(700, 400, text="The raise slider can be used\nto indicate the raise\namount. Click the 'All-In'\nbutton at the top to\nset the amount to your balance",
            font=(FONTNAME, 24), fill="white", tags="help", anchor=tk.NW, justify=CENTER)

        onTurnImage = ImageTk.PhotoImage(Image.open("../Entities/Tutorials/onTurn.png"))
        canvas.create_image(1200, 600, image=onTurnImage, anchor=tk.NW, tags="help")
        canvas.create_text(500, 700, text="The player block includes your cards, your balance\nand your position. The timer and colour of\n the block indicate when it is your go\nIf the timer runs out you will be forced a move",
            font=(FONTNAME, 24), fill="white", tags="help", anchor=tk.NW, justify=CENTER)
        
        
def loadVideo(event):
    webbrowser.open('https://www.youtube.com/watch?v=NlFguTSypBQ', new=2)

def runTutorial(window):
    global canvas, popUp, helpText, continueBtn, nextHelpLabel, prevHelpBtn, prevHelpLabel, screenIndex

    screenIndex = 0

    print("Running tutorials...")
    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.pack()
    
    #*Creating the background image
    bgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/titleBackground.png")) #path
    bg = canvas.create_image(0, 0, image=bgImage, anchor=tk.NW)

    #*Logo
    logoImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/circleLogo.fw.png")) #path
    logo = canvas.create_image(0, 0, image=logoImage, anchor=tk.NW)

    helpText = canvas.create_text(400, 400, font=(FONTNAME, 30), fill="white", text="")

    #*Continue button and label
    continueBtn = newButton(canvas, 1110, 915, "greenButton.fw.png", "continue", nextHelp)
    continueBtn.addLabel(canvas, "CONTINUE", "white", (1220, 960), 30, "continue", nextHelp)

    #*Labels underneath buttons
    nextHelpLabel = canvas.create_text(1220, 1020, font=(FONTNAME, 22), fill="white", text=allHelp[screenIndex+1])
    prevHelpLabel = canvas.create_text(510, 1020, font=(FONTNAME, 22), fill="white", text="")

    #*Main menu button
    openFunc = partial(openTitleScreen, window)
    mainmenuBtn = newButton(canvas, 100, 915, "redButton.fw.png", None, openFunc)
    mainmenuBtn.addLabel(canvas, "MAIN\nMENU", "white", (210, 960), 25, None, openFunc)

    displayHelp()

    window.mainloop()
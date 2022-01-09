#Pocket Aces gameplay
#Date started 16/12/21
#Last edited 20/12/21

#!constants
BLOCKCOLOUR = "#DFDFD0"
COLOURS = ["white","#FF2626","#D86C00","#FFFF00","#00FF00","#4D4DFF", "#FF73FF", "#FF00FF", "black"]
NINECOORDS = [(960, 680), (570, 700), (325, 515), (375, 160), (745, 70), (1150, 70), (1520, 160), (1600,515), (1370, 700)]
SIXCOORDS = [(960, 680), (375, 600), (375, 160), (960, 70), (1520, 160), (1520, 600)]
MAX9 = ["BTN", "SB", "BB", "UTG", "MP", "MP+1", "LJ", "HJ", "CO"]
MAX6 = ["BTN", "SB", "BB", "UTG", "HJ", "CO"]
NAMES = ["Hugh","Elaine","Marvin","Lonnie","Jocelyn","Joan","Edwin","Nikki","Ali","Max"]
SUITS = ["C","D","H","S"]
VALUES = [2,3,4,5,6,7,8,9,10,11,12,13,14]
STAGES = ["Preflop", "Flop", "Turn", "River", "Showdown"]
RANKS = {"HighCard": 0,
        "Pair":1,
        "TwoPair":2,
        "ThreeOfAKind":3,
        "Straight":4,
        "Flush":5,
        "FullHouse":6,
        "FourOfAKind":7,
        "StraightFlush":8}

#! imports
import random
from tkinter.constants import CURRENT
from typing import Text
from library import *
import titleScreen
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial

#!classes
class Player(object):
    def __init__(self, name, position, index, colour, x, y):
        self.hand = []
        self.name = name
        self.balance = startStack
        self.position = position
        self.ready = False
        self.index = index
        self.folded = False
        self.colour = colour
        self.currBet = 0
        self.x = x
        self.y = y

    def createBlock(self):
        #creates hexagonal block
        self.block = canvas.create_polygon(self.x, self.y, self.x+75, self.y+45, self.x+75, self.y+135
            ,self.x, self.y+180, self.x-75, self.y+135, self.x-75, self.y+45, fill=BLOCKCOLOUR, outline=self.colour, width=8)

        #adding all labels
        self.balanceLabel = canvas.create_text(self.x, self.y+120, text="$"+str(self.balance), fill=PRIMARYCOLOUR, font=(BOLDFONT,25))
        self.poslabel = canvas.create_text(self.x, self.y+150, text=str(self.position), fill=PRIMARYCOLOUR, font=(FONTNAME,15))
        self.nameLabel = canvas.create_text(self.x, self.y+200, text=str(self.name), fill=self.colour, font=(BOLDFONT,25))

    def check(self, event):
        if ROUND.currBet == 0: #validation
            self.currBet = 0
            self.ready = True
            ROUND.nextPlayer(self.index) #moving to next player

    def betRaise(self, amount, event):
        if amount >= self.balance: #ALL IN
            self.ready = True
            self.currBet = self.balance
            self.updateBal(self.currBet)
            ROUND.nextPlayer(self.index ) #moving to next player
        elif amount >= ROUND.currBet * 2: #valid raise
            for player in allPlayers:
                if player.balance != 0 and not player.folded: #still can play in this round
                    player.ready = False
            self.ready = True
            self.currBet = amount
            self.updateBal(amount)
            ROUND.currBet = amount
            ROUND.nextPlayer(self.index)  #moving to next player

    def call(self, event):
        amount = ROUND.currBet
        if amount >= self.balance: #ALL IN
            self.betRaise(amount, None)
        elif amount == 0:
            self.check(None)
        elif amount < self.balance: #normal call
            self.ready = True
            self.currBet = amount
            self.updateBal(amount)
            ROUND.nextPlayer(self.index) #moving to next player

    def fold(self, event):
        self.ready = True
        self.currBet = 0
        self.folded = True
        ROUND.nextPlayer(self.index) #moving to next player

    def force(self):
        if ROUND.currBet == 0: #checking if we can check
            self.check(None)
        elif ROUND.currBet > 0: #cannot check
            self.fold(None)

    def updateBal(self, amount):
        self.balance -= amount #updating balance
        #*updating widgets
        canvas.itemconfigure(self.balanceLabel, text="$"+str(self.balance))
        ROUND.updatePot(amount)

    def bestRank(self):
        pass

    def currTurn(self): #TODO
        #*editing block
        canvas.itemconfigure(self.block, fill=PRIMARYCOLOUR, outline="white")
        canvas.itemconfigure(self.poslabel, fill="white")
        canvas.itemconfigure(self.balanceLabel, fill="white")

        #TODO create timer

    def endTurn(self): #TODO
        #*editing block
        canvas.itemconfigure(self.block, fill=BLOCKCOLOUR, outline=self.colour)
        canvas.itemconfigure(self.poslabel, fill=PRIMARYCOLOUR)
        canvas.itemconfigure(self.balanceLabel, fill=PRIMARYCOLOUR)

        #TODO get rid of timer
        ROUND.nextPlayer(self.index)

class User(Player):
    def __init__(self, name, position, index, colour, x, y):
        super().__init__(name, position, index, colour, x, y)
        self.preSelect = preSelectButtons(canvas)

    def createBlock(self):
        #creates hexagonal block
        self.block = canvas.create_polygon(self.x, self.y, self.x+125, self.y+75, self.x+125, self.y+220
            ,self.x, self.y+295, self.x-125, self.y+220, self.x-125, self.y+75, fill=BLOCKCOLOUR, outline=PRIMARYCOLOUR, width=10)

        #adding all labels
        self.balanceLabel = canvas.create_text(self.x, self.y+200, text="$"+str(self.balance), fill=PRIMARYCOLOUR, font=(BOLDFONT,35))
        self.poslabel = canvas.create_text(self.x, self.y+240, text=str(self.position), fill=PRIMARYCOLOUR, font=(FONTNAME,25))
        self.nameLabel = canvas.create_text(self.x, self.y+320, text=str(self.name), fill=self.colour, font=(BOLDFONT,35))
        
    def currTurn(self):
        super().currTurn()

        if self.preSelect.get() == 5: #no preselect button selected
            self.preSelect.hide(canvas) #hiding preselect buttons

            #*creating raise slider
            self.raiseSlider = tk.Scale(canvas, from_=self.balance, to=0, font=(FONTNAME,30), bg="green", length=400
                ,showvalue=0, orient=tk.VERTICAL, command=self.sliderUpdate, troughcolor="#00FF00", width=30, bd=0)
            self.raiseSlider.place(x=100, y=450)
            self.raiseLabel = canvas.create_text(110,875, text="$"+str(self.raiseSlider.get()),fill="#00FF00",font=(FONTNAME,30), tags="actions")

            #*creating the buttons
            self.raiseBtn = newButton(canvas, 60, 930, "Action/raise.fw.png", "actions", self.betRaise)
            self.checkBtn = newButton(canvas, 370, 930, "Action/check.fw.png", "actions", self.check)
            self.callBtn = newButton(canvas, 1300, 930, "Action/call.fw.png", "actions", self.call)
            self.foldBtn = newButton(canvas, 1610, 930, "Action/fold.fw.png", "actions", self.fold)
        elif self.preSelect.get() == 0: #FOLD
            self.fold(None)
        elif self.preSelect.get() == 1: #CHECK
            self.check(None)
        elif self.preSelect.get() == 2 or self.preSelect.get() == 3: #CALL OR CALL ANY
            self.call(None)

    def sliderUpdate(self, event):
        #*Updating label for raise amount
        labelText = "$"+str(self.raiseSlider.get())
        canvas.itemconfigure(self.raiseLabel, text=labelText)

    def betRaise(self, event):
        amount = self.raiseSlider.get() #getting raise amount
        super().betRaise(amount, event)

    def endTurn(self):
        super().endTurn()

        #*placing pre select buttons
        self.preSelect.place(canvas)

        #*deleting action buttons
        canvas.delete("actions")
        canvas.delete(self.raiseSlider)

class AI(Player):
    def __init__(self, name, position, index, colour, x, y):
        super().__init__(name, position, index, colour, x, y)
        self.tutor = Tutor(1)
    
    def currTurn(self):
        super().currTurn()
        self.chooseMove() #playing a move

    def chooseMove(self):
        pass

class Card(object):
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

        #*finding the image name
        if self.value <= 9:
            self.name = str(self.value) + self.suit
        elif self.value == 10:
            self.name = "T"+self.suit
        elif self.value == 11:
            self.name = "J"+self.suit
        elif self.value == 12:
            self.name = "Q"+self.suit
        elif self.value == 13:
            self.name = "K"+self.suit
        elif self.value == 14:
            self.name = "A"+self.suit

        self.img = Image.open("../Entities/Cards/Front Faces/"+self.name+".png")
        self.physImage = ImageTk.PhotoImage(self.img)

    def place(self, xCoOrd, yCoOrd):
        #creates card image on screen
        self.displayedCard = canvas.create_image(xCoOrd, yCoOrd, image=self.physImage)

    def enlarge(self, xCoOrd, yCoOrd):
        self.img = self.img.resize((135,180), Image.ANTIALIAS) #resizing image
        self.physImage = ImageTk.PhotoImage(self.img) 
        self.place(xCoOrd, yCoOrd) #displaying image

    def flip(self, xCoOrd, yCoOrd):
        self.img = Image.open("../Entities/Cards/Backs/"+texturePack+".fw.png") #changing image
        self.physImage = ImageTk.PhotoImage(self.img)
        self.place(xCoOrd, yCoOrd) #displaying image

class Deck(object):
    def __init__(self):
        self.cards = []
        self.used = []
    
    def dealPlayer(self, amount, player):
        xCoOrd = player.x - 25
        yCoOrd = player.y

        #*dealing cards
        for i in range(0,amount):
            index = random.randint(0, len(self.cards)-1) #choosing a random card
            player.hand.append(self.cards[index]) #adding random card to location
            self.used.append(self.cards.pop(index)) #removing card and adding to used

            #*displaying card
            if type(player) is User: #users hand should be displayerd
                player.hand[-1].enlarge(xCoOrd, yCoOrd+75)
            else: #opponents hands should remain hidden
                player.hand[-1].flip(xCoOrd, yCoOrd+50)
            xCoOrd+=50

    def dealCommunity(self):
        #*Changing variables depending on current stage
        if ROUND.stage == "Flop":
            amount = 3
            xCoOrd = 785
        elif ROUND.stage == "Turn":
            amount = 1
            xCoOrd = 950
        elif ROUND.stage == "River":
            amount = 1
            xCoOrd = 100
        yCoOrd = 490
        
        #*dealing cards
        for i in range(0, amount):
            index = random.randint(0, len(self.cards)-1) #choosing a random card
            ROUND.community.append(self.cards[index]) #adding random card to location
            self.used.append(self.cards.pop(index)) #removing card and adding to used
            ROUND.community[-1].place(xCoOrd, yCoOrd) #displaying card
            xCoOrd+=90
        
class Round(object):
    def __init__(self):
        self.community = []
        self.pot = 0
        self.stage = STAGES[0]
        self.bigBlind = 10
        self.currPlayer = 1
        self.currBet = 0

        #*Pot
        self.potImage = ImageTk.PhotoImage(Image.open("../Entities/Chips/potChips.png"))
        self.physPot = canvas.create_image(850, 360, image=self.potImage, anchor=tk.NW)

        self.potLabel = canvas.create_text(940, 390, text="$"+str(self.pot), font=(FONTNAME,30), fill="#00FFFF")

    def nextStage(self):
        #*incrementing stage
        try:
            self.stage = STAGES[STAGES.index(self.stage)+1]
        except IndexError: #reached the final stage
            self.stage = STAGES[0] #set stage to first stage
            self.newRound() #initiate a new round
        
        #preparing each player for next stage
        for player in allPlayers:
            if player.position == "SB":
                self.currPlayer = player.index #setting the action to the small blind
            if not player.folded: #if player still in round
                player.ready = False
                player.currBet = 0

        #automatically dealing community cards
        if ROUND.stage in ["Flop","Turn","River"]:
            DECK.dealCommunity()

        self.currBet = 0

    def newRound(self):
        winner = allPlayers[self.calcWinner()] #find which player has won
        winner.balance += self.pot

        #resetting deck
        for card in DECK.used:
            DECK.cards.append(card)

        #resetting variables
        DECK.used = []
        self.community = []
        self.currBet = 0
        self.pot = 0

        #preparing for new round
        for player in allPlayers:
            #*incrementing each players position
            try:
                player.position = allPositions[allPositions.index(player.position)+1]
            except:
                player.position = allPositions[0]

            #automatically dealing blinds and setting current position
            if player.position == "SB":
                player.betRaise(self.bigBlind/2, None)
            elif player.position == "BB":
                player.betRaise(self.bigBlind, None)
            elif player.position == "UTG":
                self.currPlayer = player.index

            #resetting player attributes
            player.hand = []
            player.ready = False
            player.currBet = 0
            player.folded = False
            DECK.dealPlayer(2, player)

    def nextPlayer(self, index):
        player = allPlayers[index]

        #*finding the next player who has not folded
        while True:
            #*looping to the next player
            index+=1
            try:
                player = allPlayers[index]
            except:
                player = allPlayers[0]
                index = 0
            
            if not player.folded: #if the player has not folded
                break

        #*checking to see if we need to move to the next stage
        if player.ready:
            self.nextStage()
        else:
            self.currPlayer = index
            
    def updatePot(self, amount):
        self.pot += amount #updating pot
        #*updating widgets
        canvas.itemconfigure(self.potLabel, text="$"+str(self.pot))

class Tutor(object):
    def __init__(self, level):
        self.level = level #0-2 represent AI levels

        #level 3 represents tutor used by user
        if self.level == 3:
            self.createIcons()

    def createIcons(self):
        self.headImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/head.png"))
        self.head = canvas.create_image(1650, 25, image=self.headImage, anchor=tk.NW)
        self.expand = newButton(canvas, 1680, 290, "expand.png", "tutor", self.extend)
        #TODO self.extend should open up help section

    def extend(self, event):
        buttonPressSound.play()

    def calcEV(self):
        pass

#!subprograms
def openNewGame(window, event):
    buttonPressSound.play()
    canvas.destroy()
    titleScreen.runTitleScreen(window)
    exit()

def ingameSettings(event):
    buttonPressSound.play()

def createGameplay(window):
    global canvas, startStack, texturePack, allPlayers, allCoOrds, allPositions, potLabel

    allPositions = []
    allCoOrds = []
    allPlayers = []

    print("Running gameplay...")
    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.pack()

    settings = readJson("Settings.json")
    startStack = (settings["options"]["StartStack"])*10
    numPlayers = int(settings["options"]["MaxPlayer"])
    
    #*Creating the background image
    texturePack = settings["settings"]["TexturePack"]
    bgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/Gameplay/"+texturePack+".png")) #path
    bg = canvas.create_image(0, 0, image=bgImage, anchor=tk.NW)

    #*Table
    tableImage = ImageTk.PhotoImage(Image.open("../Entities/Table/"+texturePack+".png"))
    table = canvas.create_image(280, 150, image=tableImage, anchor=tk.NW)

    #*Deck
    deckImage = ImageTk.PhotoImage(Image.open("../Entities/Cards/Decks/"+texturePack+".fw.png"))
    deck = canvas.create_image(680, 490, image=deckImage)

    #*Buttons
    exitFunc = partial(openNewGame, window)
    exitButton = newButton(canvas, 50, 40, "exitDoor.png", None, exitFunc)

    #TODO create in-game settings menu
    settingsButton = newButton(canvas, 60, 220, "settingsCog.png", None, ingameSettings)

    #*Tutor
    if settings["settings"]["Tutor"] == "ON":
        userTutor = Tutor(3)

    runGameplay(window)

def runGameplay(window):
    global DECK, ROUND, allPositions, allCoOrds

    #*Creating deck of cards
    DECK = Deck()

    for suit in SUITS:
        for value in VALUES:
            DECK.cards.append(Card(suit, value))

    #*getting number of players
    maxPlayers = int(getJson("Settings.json", ("options","MaxPlayer")))
    if maxPlayers == 9: #changing variable sto fit with number of players
        allPositions = MAX9[:]
        allCoOrds = NINECOORDS[:]
    elif maxPlayers == 6:
        allPositions = MAX6[:]
        allCoOrds = SIXCOORDS[:]

    #*starting round
    ROUND = Round()

    #*creating player object
    for i in range(0,maxPlayers):
        if i == 0:
            allPlayers.append(User("You", allPositions[i], i, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
        else:
            allPlayers.append(AI(NAMES[i], allPositions[i], i, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
        allPlayers[-1].createBlock()
        
        #*automatically dealing blinds
        if allPlayers[-1].position == "SB":
                allPlayers[-1].betRaise(ROUND.bigBlind//2, None)
        elif allPlayers[-1].position == "BB":
            allPlayers[-1].betRaise(ROUND.bigBlind, None)
        elif allPlayers[-1].position == "UTG":
            ROUND.currPlayer = allPlayers[-1].index
            allPlayers[-1].currTurn()
        
    for player in allPlayers:
        DECK.dealPlayer(2, player)

    #ROUND.nextStage()

    window.mainloop()

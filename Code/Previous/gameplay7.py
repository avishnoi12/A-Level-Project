#Pocket Aces gameplay
#Date started 20/12/21
#Last edited 28/1/22

#!constants
BLOCKCOLOUR = "#DFDFD0"
COLOURS = ["white","#FF2626","#D86C00","#FFFF00","#00FF00","#4D4DFF", "#FF73FF", "#FF00FF", "black"]
NINECOORDS = [(960, 680), (570, 700), (325, 515), (375, 160), (745, 70), (1150, 70), (1520, 160), (1600,515), (1370, 700)]
SIXCOORDS = [(960, 680), (375, 600), (375, 160), (960, 70), (1520, 160), (1520, 600)]
MAX9 = ["BTN", "SB", "BB", "UTG", "MP", "MP+1", "LJ", "HJ", "CO"]
MAX6 = ["BTN", "SB", "BB", "UTG", "HJ", "CO"]
NAMES = ["Gareth","Sue","Steve","Iain","Vin","Wendy","Tim","James","Paul","Caroline"]
SUITS = ["C","D","H","S"]
VALUES = [2,3,4,5,6,7,8,9,10,11,12,13,14]
STAGES = ["Preflop", "Flop", "Turn", "River"]
RANKS = {"HighCard": 0,
        "Pair":1,
        "TwoPair":2,
        "ThreeOfAKind":3,
        "Straight":4,
        "Flush":5,
        "FullHouse":6,
        "FourOfAKind":7,
        "StraightFlush":8}
ORDERREMOVE = ["MP+1", "MP", "LJ", "HJ", "CO", "UTG", "BB", "SB", "BTN"]
ALLAILEVELS = {"EXPERT": 2, "PRO": 1, "NOVICE": 0}

#! imports
from decimal import ROUND_DOWN
import random
from re import A, X
import threading
from tkinter import ANCHOR, HORIZONTAL, ttk
import server as srvr
import client as clnt
import socket
from library import *
import titleScreen
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial
import os

AILEVEL = ALLAILEVELS[getJson("Settings.json", ("options","AI Level"))]
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
        self.allIn = False
        self.colour = colour
        self.currBet = 0
        self.x = x
        self.y = y
        self.iconLabel = canvas.create_text(self.x+130,self.y+50, font=(BOLDFONT, 30), anchor=tk.NW)

    def createBlock(self):
        #creates hexagonal block
        self.block = canvas.create_polygon(self.x, self.y, self.x+75, self.y+45, self.x+75, self.y+135
            ,self.x, self.y+180, self.x-75, self.y+135, self.x-75, self.y+45, fill=BLOCKCOLOUR, outline=self.colour, width=8)

        #adding all labels
        self.balanceLabel = canvas.create_text(self.x, self.y+120, text="$"+str(self.balance), fill=PRIMARYCOLOUR, font=(BOLDFONT,25))
        self.posLabel = canvas.create_text(self.x, self.y+150, text=str(self.position), fill=PRIMARYCOLOUR, font=(FONTNAME,15))
        self.nameLabel = canvas.create_text(self.x, self.y+200, text=str(self.name), fill=self.colour, font=(BOLDFONT,25))

    def check(self, event):
        if ROUND.currBet == 0: #validation
            self.currBet = 0
            self.ready = True
            self.placeIcon("check") #updating GUI
            checkSound.play()
            self.endTurn()
            
    def betRaise(self, amount, event):
        if amount >= self.balance: #ALL IN
            #*everyone who was ready is no longer ready
            for player in allPlayers:
                if player.balance != 0 and not player.folded and player.currBet < self.balance: #still can play in this round
                    player.ready = False
            self.ready = True
            self.currBet += self.balance
            ROUND.currBet = self.currBet
            self.updateBal(self.balance)
            ROUND.allIn = True
            self.allIn = True

            #*updating GUI
            raiseSound.play()
            self.placeIcon("allIn1.fw")
            THEUSER.updatePreSelect()
            #ROUND.numPlayersLeft()
            self.endTurn()
        elif amount == 0:
            self.check(None)
        elif amount >= ROUND.currBet * 2 and amount >= ROUND.bigBlind: #valid raise
            #*everyone who was ready is no longer ready
            for player in allPlayers:
                if player.balance != 0 and not player.folded and player.currBet < amount: #still can play in this round
                    player.ready = False
            self.ready = True
            self.currBet += amount
            self.updateBal(amount)
            ROUND.currBet = self.currBet

            #*updating GUI
            self.placeIcon("raise")
            THEUSER.updatePreSelect()
            self.endTurn()
            raiseSound.play()

    def call(self, event):
        amount = ROUND.currBet
        print("[CALL AMOUNT] " + str(amount))
        if amount >= self.balance: #ALL IN
            self.betRaise(amount, None)
        elif amount == 0:
            self.check(None)
        elif amount < self.balance: #normal call
            self.ready = True
            amount = amount-self.currBet
            self.currBet += amount
            self.updateBal(amount)

            #*updating GUI
            self.placeIcon("call")
            callSound.play()

            self.endTurn()

    def fold(self, event):
        self.ready = True
        self.currBet = 0
        self.folded = True
        
        #*updating GUI
        self.placeIcon("fold")
        for card in self.hand:
            card.unplace()
        foldSound.play()
        
        #*checking if only one player left
        #ROUND.numPlayersLeft()

        self.endTurn()
        canvas.itemconfigure(self.block, outline="grey")

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

    def bestRank(self, community):
        totalCards = self.hand + community #combining community and hole cards
        ##print("[TOTAL CARDS] "+str(totalCards))
        straight = self.hasStraight(totalCards) #do they have a straight
        if straight != []: # they have a straight
            #checking if they have a straight flush, flush or just a straight
            draw, rank = self.hasStraightFlush(totalCards, straight)
        elif self.hasSameCard(totalCards, 3): #if they have AT LEAST a TOAK
            if self.hasSameCard(totalCards, 4) == "Exact": #EXACTLY  a FOAK
                rank =  "FourOfAKind"
                draw = self.sameCardHand(totalCards, 4)
            elif self.hasSameCard(totalCards, 2) == "Exact": #full house
                rank = "FullHouse"
                draw = self.sameCardHand(totalCards, 2)
            elif self.hasFlush(totalCards) != []: #if they have a flush
                rank = "Flush"
                draw = self.hasFlush(totalCards)
            else:
                rank = "ThreeOfAKind"
                draw= self.sameCardHand(totalCards, 3)
        elif self.hasFlush(totalCards) != []: #if they have a flush
            rank = "Flush"
            draw = self.hasFlush(totalCards)
        elif self.hasSameCard(totalCards, 2): #AT LEAST a pair
            if self.hasTwoPair(totalCards):
                rank = "TwoPair"
            else:
                rank = "Pair"
            draw = self.sameCardHand(totalCards, 2)
        else:
            rank = "HighCard"
            draw = self.highestValue(totalCards, 5)

        return draw, rank

    def hasFlush(self, totalCards):
        suits = ["C","D","H","S"]
        draw = []
        cardSuits = []

        #*creating an array of just suits
        for card in totalCards:
            cardSuits.append(card.suit)

        #*repeating for every suit
        for suit in suits:
            if cardSuits.count(suit) >= 5: #at least 5 cards of same suit
                for card in totalCards:
                    if card.suit == suit:
                        draw.append(card)

                draw = self.highestValue(draw, 5) #selecting topp 5 cards only
        return draw
            
    def hasSameCard(self, totalCards, amount):
        ofAKind = False
        cardsValue = []

        #*creating an array of just values
        for card in totalCards:
            cardsValue.append(card.value)

        #*repeating for every card
        for card in cardsValue:
            count = cardsValue.count(card) #counting how many cards of same value
            if count == amount: #exact required amount
                ofAKind = "Exact"
            elif count > amount: #more than required amount
                ofAKind = "Greater"
        return ofAKind

    def hasStraight(self, totalCards):
        cardsvalue = []
        answer = []

        #*creating an array of values with NO repeats
        for card in totalCards:
            if card.value not in cardsvalue:
                cardsvalue.append(card.value)

        #*if there is an ace in the hand make sure it can be treated as a '1'
        if 14 in cardsvalue:
            cardsvalue.append(1)

        #*if there are more than 5 cards to look from - a straight is possible
        if len(cardsvalue) >= 5:
            cardsvalue.sort() #sorting the values
            for start in range(0,len(cardsvalue)-4): #repeating for how many combinations there are
                straight = True
                for i in range(start, start+4): #repeating for 4 out of 5 cards
                    if cardsvalue[i+1]-1 != cardsvalue[i]: #if the card is not connected to the next card
                        straight = False
                        break
                if straight: #if these cards make a straight
                    answer = cardsvalue[start:start+5]
        return answer
                
    def hasStraightFlush(self, totalCards, straight):
        flushDraw = self.hasFlush(totalCards) #checking if they ahve a flush
        answer = True
        draw = []

        #*if they do have a flush
        if flushDraw != []:
            #checking if the straight and the flush coincide
            for card in flushDraw:
                if card.value not in straight:
                    answer = False
            
            #*Deciding which rank they have
            if answer:
                type = "StraightFlush"
            else:
                type = "Flush"
            draw = flushDraw
        else: #did not have a flush
            type = "Straight"
            draw = self.straightHand(totalCards, straight)
        return draw, type

    def hasTwoPair(self, totalCards):
        answer = False
        cardsValue = []
        used = []
        amount = 0

        #*creating an array of just values
        for card in totalCards:
            cardsValue.append(card.value)

        #*repeating for every card
        for card in cardsValue:
            count = cardsValue.count(card) #counting how many cards with same value
            if count == 2 and card not in used: #a NEW pair
                amount += 1
                used.append(card)

        if amount >=2: #if there is at least two distinct pair
            answer = True
        return answer

    def currTurn(self):
        #print("[CURR TURN] "+str(self.index))
        #*editing block
        canvas.itemconfigure(self.block, fill=PRIMARYCOLOUR, outline="white")
        canvas.itemconfigure(self.posLabel, fill="white")
        canvas.itemconfigure(self.balanceLabel, fill="white")

        #validates only one timer exists at one point
        try:
            self.timer.destroy()
        except:
            self.timer = ttk.Progressbar(canvas, orient=HORIZONTAL, length=200, mode="determinate")
        else:
            self.timer = ttk.Progressbar(canvas, orient=HORIZONTAL, length=200, mode="determinate")

        if not ROUND.timerHide: #if ingame settings is not open
            self.createTimer()

    def createTimer(self):
        ##print("[TIMER] "+ str(self.index))
        self.timer.place(x=self.x-100, y=self.y-40)

    def hideTimer(self):
        try: #validation
            self.timer.place_forget()
        except:
            pass

    def endTurn(self):
        #print("[END TURN] "+str(self.index)+", Current: "+str(ROUND.currPlayer))
        #*editing block
        canvas.itemconfigure(self.block,outline=self.colour,fill=BLOCKCOLOUR)
        canvas.itemconfigure(self.posLabel, fill=PRIMARYCOLOUR)
        canvas.itemconfigure(self.balanceLabel, fill=PRIMARYCOLOUR)
        self.timer.destroy()

    def placeBB(self): #places big blind
        for player in allPlayers:
            if player.balance != 0 and not player.folded: #still can play in this round
                player.ready = False
        self.ready = True
        self.currBet = ROUND.bigBlind
        self.updateBal(self.currBet)
        ROUND.currBet = self.currBet
        #*updating GUI
        self.placeIcon("raise")
        THEUSER.updatePreSelect()

    def placeSB(self): #places small blind
        self.ready = True
        self.currBet = ROUND.bigBlind//2
        self.updateBal(self.currBet)
        #ROUND.currBet = self.currBet
        #*updating GUI
        self.placeIcon("raise")
        THEUSER.updatePreSelect()

    def placeIcon(self, imgPath):
        #*updating icon image
        self.iconImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/Action/"+imgPath+".png"))
        self.icon = canvas.create_image(self.x+70, self.y+50, image=self.iconImage, anchor=tk.NW)

        #*updating icon label
        if imgPath == "call":
            canvas.itemconfigure(self.iconLabel, text="$"+str(self.currBet), fill="#09ffff")
        elif imgPath == "raise":
            canvas.itemconfigure(self.iconLabel, text="$"+str(self.currBet), fill="#00ff00")
        elif imgPath == "fold" or imgPath == "check":
            canvas.itemconfigure(self.iconLabel, text="")
        elif imgPath == "allIn1.fw":
            canvas.itemconfigure(self.iconLabel, text="$"+str(self.currBet), fill="#09ffff")

    def unplaceIcon(self):
        try: #validating icons existence
            canvas.delete(self.icon)
            canvas.itemconfigure(self.iconLabel, text="")
        except:
            pass

    def remCards(self):
        allCards = DECK.cards[:] + DECK.used[:] #full deck of 52 cards
        totalCards = self.hand[:] + ROUND.community[:]
        toRemove = [] #array of all cards to remove

        #finding the cards to remove
        for card in allCards:
            for each in totalCards:
                if card.suit == each.suit and card.value == each.value:
                    toRemove.append(card)

        #removing the cards you see from the total deck
        for card in toRemove:
            allCards.remove(card)

        return allCards

    def timerUpdate(self, count):
        try:
            self.timer['value'] += 10 #validating timer exists
        except:
            pass #stops the recursive call
        else:
            if count < 9: #if timer hasnt reached its limit
                canvas.after(1000, self.timerUpdate, count+1)
            else: #timer has reached its limit
                self.force() #force a move

    def highestValue(self, totalCards, amCards):
        #*Returns highest value cards
        #*Also sorts the cards
        values = []
        draw = []
        
        #*Creating array of just values
        for card in totalCards:
            values.append(card.value)

        #*Adding specified amount of cards to their draw
        for i in range(amCards):
            maxIndex = values.index(max(values)) #index of highest value
            draw.append(totalCards.pop(maxIndex)) #adding to return arrray
            values.pop(maxIndex) #removing value

        return draw

    def straightHand(self, totalCards, straight):
        draw = []

        for card in totalCards:
            if card.value in straight: #if the card makes uo a straight
                #add it to the best hand
                straight.remove(card.value)
                draw.append(card)
            elif card.value == 14 and 1 in straight: #*Special case
                #an Ace is counted as a 1 in the straight
                straight.remove(1)
                draw.append(card)
        return draw

    def sameCardHand(self, totalCards, amount):
        cardsValue = []
        draw = []

        #*creating an array of just values
        for card in totalCards:
            cardsValue.append(card.value)
        cardsValue.sort(reverse=True) #sorting in desc order

        #*repeating for every card
        for value in cardsValue:
            count = cardsValue.count(value) #counting how many cards of same value
            if count == amount and len(draw) < 4: #prevents adding too many cards
                #*adds the pair/TOAK/FOAK
                for card in totalCards:
                    if card.value == value:
                        totalCards.remove(card)
                        draw.append(card)
        
        remaining = 5 - len(draw) #how many cards need to be added
        draw = draw + self.highestValue(totalCards, remaining) #adding highest value cards
        return draw

    def eliminatePlayer(self):
        #removing player from allPlayers array
        #print("[ELIM] "+str(self.name))
        allPlayers.remove(self)

        #updating GUI
        canvas.delete(self.block, self.balanceLabel, self.posLabel, self.nameLabel)
        self.unplaceIcon()

        #removing next position from the allPosition array
        for pos in ORDERREMOVE:
            if pos in allPositions:
                allPositions.remove(pos)
                break

    def updateIndex(self, newIndex):
        self.index = newIndex

        #validating existence of tutor
        try:
            self.tutor.index = newIndex #updating tutor index
        except:
            pass

    def __repr__(self) -> str:
        return self.name

class User(Player):
    def __init__(self, name, position, index, colour, x, y):
        super().__init__(name, position, index, colour, x, y)
        self.preSelect = preSelectButtons(canvas)

        #*Tutor
        if getJson("Settings.json", ("settings","Tutor")) == "ON":
            if clnt.clientExists(): #multiplayer game
                if assistsAllowed == "ON": #tutor is allowed
                    self.tutor = Tutor(3, index)
            else: #singleplayer game
                self.tutor = Tutor(3, index)

    def createBlock(self):
        #creates hexagonal block
        self.block = canvas.create_polygon(self.x, self.y, self.x+125, self.y+75, self.x+125, self.y+220
            ,self.x, self.y+295, self.x-125, self.y+220, self.x-125, self.y+75, fill=BLOCKCOLOUR, outline=PRIMARYCOLOUR, width=10)

        #adding all labels
        self.balanceLabel = canvas.create_text(self.x, self.y+200, text="$"+str(self.balance), fill=PRIMARYCOLOUR, font=(BOLDFONT,35))
        self.posLabel = canvas.create_text(self.x, self.y+240, text=str(self.position), fill=PRIMARYCOLOUR, font=(FONTNAME,25))
        self.nameLabel = canvas.create_text(self.x, self.y+320, text=str(self.name), fill=self.colour, font=(BOLDFONT,35))

        timerStyle = ttk.Style()
        timerStyle.theme_use('clam')
        barColour = getJson("Settings.json",("settings","TexturePack")).lower()
        timerStyle.configure("Horizontal.TProgressbar", background=barColour, troughcolor="white", 
            bordercolor="white", darkcolor=barColour, lightcolor=barColour)
        
    def currTurn(self):
        super().currTurn()
        
        #self.preSelect.hide(canvas) #hiding preselect buttons
        canvas.delete("preSelect")

        if self.preSelect.get() == 5: #no preselect button selected

            #*placing slider and label
            self.raiseSlider = tk.Scale(canvas, from_=self.balance, to=0, font=(FONTNAME,30), bg="green", length=400
                ,showvalue=0, orient=tk.VERTICAL, command=self.sliderUpdate, troughcolor="#00FF00", width=30, bd=0)
            self.raiseSlider.place(x=100, y=450)
            self.raiseLabel = canvas.create_text(110,875, text="$"+str(self.raiseSlider.get()),fill="#00FF00",font=(FONTNAME,30), tags="actions")

            #*creating the buttons
            raiseFunc = partial(self.betRaise, None)
            self.raiseBtn = newButton(canvas, 60, 930, "Action/raise.fw.png", "actions", raiseFunc)
            self.checkBtn = newButton(canvas, 1300, 930, "Action/check.fw.png", "actions", self.check)
            self.callBtn = newButton(canvas, 370, 930, "Action/call.fw.png", "actions", self.call) 
            self.foldBtn = newButton(canvas, 1610, 930, "Action/fold.fw.png", "actions", self.fold)

            self.timerUpdate(0)
        elif self.preSelect.get() == 3: #FOLD
            self.preSelect.deselect(canvas)
            self.fold(None)
        elif self.preSelect.get() == 2: #CHECK
            self.preSelect.deselect(canvas)
            self.check(None)
        elif self.preSelect.get() == 0 or self.preSelect.get() == 1: #CALL OR CALL ANY
            self.preSelect.deselect(canvas)
            self.call(None)

    def sliderUpdate(self, event):
        #*Updating label for raise amount
        labelText = "$"+str(self.raiseSlider.get())
        canvas.itemconfigure(self.raiseLabel, text=labelText)

    def betRaise(self, amount, event):
        if amount is None:
            amount = self.raiseSlider.get() #getting raise amount

        if clnt.clientExists(): #multiplayer game - so need to send move to server
            moveData = str({'Move':{'move':"RAISE", 'name': self.name, 'amount': amount}})
            clnt.sendMessage(moveData.encode(FORMAT)) #sending the server our move

        super().betRaise(amount, event)

    def fold(self, event):
        if clnt.clientExists(): #multiplayer game - so need to send move to server
            moveData = str({'Move':{'move':"FOLD", 'name': self.name}})
            clnt.sendMessage(moveData.encode(FORMAT)) #sending the server our move

        super().fold(event)
        self.preSelect.hide(canvas)

    def call(self, event):
        if clnt.clientExists(): #multiplayer game - so need to send move to server
            moveData = str({'Move':{'move':"CALL", 'name': self.name}})
            clnt.sendMessage(moveData.encode(FORMAT)) #sending the server our move

        super().call(event)

    def check(self, event):
        if clnt.clientExists(): #multiplayer game - so need to send move to server
            moveData = str({'Move':{'move':"CHECK", 'name': self.name}})
            clnt.sendMessage(moveData.encode(FORMAT)) #sending the server our move
        
        super().check(event)

    def endTurn(self):
        if ROUND.currPlayer == self.index: #validating it is our turn
            super().endTurn()
            canvas.itemconfigure(self.block, outline=PRIMARYCOLOUR)

            #*placing pre select buttons
            if not self.folded:
                self.preSelect.place(canvas)

            #*deleting action buttons
            canvas.delete("actions")
            try: #validating slider exists
                self.raiseSlider.place_forget() #deleting slider
            except AttributeError:
                pass

            ROUND.nextPlayer(self.index)

    def updatePreSelect(self):
        self.preSelect.disable(canvas, 2) #greying out check button
        if self.preSelect.get() == 2: #call selected when a raise is played
            self.preSelect.deselect(canvas)

    def pauseTurn(self):
        #Pauses the turn for the showdown
        #does not trigger next player
        ##print("[PAUSE TURN] "+str(self.index))
        super().endTurn()
        canvas.itemconfigure(self.block, outline=PRIMARYCOLOUR)
        
    def eliminatePlayer(self):
        global elimPopUp, popUpLeave

        super().eliminatePlayer()
        elimPopUp = newPopUp(canvas, "You have been eliminated")

        #*Creating buttons
        popUpLeave = newButton(canvas, 500, 660, "greenButton.fw.png", "popUp", closePopUp)
        popUpLeave.addLabel(canvas, "OK", "white", (615, 700), 30, "popUp", closePopUp)
       
class AI(Player):
    def __init__(self, name, position, index, colour, x, y):
        super().__init__(name, position, index, colour, x, y)
        self.tutor = Tutor(AILEVEL, index)
    
    def currTurn(self):
        super().currTurn()
        self.chooseMove()

    def endTurn(self):
        if ROUND.currPlayer == self.index: #validating it is our turn
            super().endTurn()
            ROUND.nextPlayer(self.index)

    def pauseTurn(self):
        #Pauses the turn for the showdown
        ##print("[PAUSE TURN] "+str(self.index))
        #does not trigger next player
        super().endTurn()
         
    def chooseMove(self):
        self.timerUpdate(0)

        timeToMove = random.randint(1000, 9000) #how much time taken to move
        move = self.tutor.optimalMove() #calculating move

        print(f"{self.name} plays {move}")

        #*Executing the move
        if move == "CALL":
            canvas.after(timeToMove, self.call, None)
        elif move == "CHECK":
            canvas.after(timeToMove, self.check, None)
        elif move == "FOLD":
            canvas.after(timeToMove, self.fold, None)
        elif move == "MINRAISE":
            if ROUND.currBet == 0:
                canvas.after(timeToMove, self.betRaise, ROUND.bigBlind ,None)
            else:
                canvas.after(timeToMove, self.betRaise, ROUND.currBet*2, None)
        elif move == "HALFRAISE":
            canvas.after(timeToMove, self.betRaise, self.balance//2 ,None)
        elif move == "ALLIN":
            canvas.after(timeToMove, self.betRaise, self.balance, None)

class multiPlayer(Player):
    def __init__(self, name, position, index, colour, x, y):
        super().__init__(name, position, index, colour, x, y)

    def endTurn(self):
        if ROUND.currPlayer == self.index: #validatiing it is our turn
            super().endTurn()
            ROUND.nextPlayer(self.index)
        
    def pauseTurn(self):
        #Pauses the turn for the showdown
        #does not trigger next player
        super().endTurn()

    def currTurn(self):
        super().currTurn()
        self.timerUpdate(0)

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

    def unplace(self):
        try:
            canvas.delete(self.displayedCard)
        except AttributeError:
            pass

    def enlarge(self, xCoOrd, yCoOrd):
        self.img = self.img.resize((135,180), Image.ANTIALIAS) #resizing image
        self.physImage = ImageTk.PhotoImage(self.img) 
        self.place(xCoOrd, yCoOrd) #displaying image

    def flip(self, xCoOrd, yCoOrd):
        self.img = Image.open("../Entities/Cards/Backs/"+texturePack+".fw.png") #changing image
        self.physImage = ImageTk.PhotoImage(self.img)
        self.place(xCoOrd, yCoOrd) #displaying image

    def reveal(self):
        self.img = Image.open("../Entities/Cards/Front Faces/"+self.name+".png") #changing image
        self.physImage = ImageTk.PhotoImage(self.img)
        canvas.itemconfigure(self.displayedCard, image=self.physImage) #displaying image

    def __repr__(self) -> str:
        return self.name

class Deck(object):
    def __init__(self):
        self.cards = []
        self.used = []
        self.cardData = {"Hand": {}}
    
    def dealPlayer(self, amount, player):
        xCoOrd = player.x - 25
        yCoOrd = player.y

        #print(clnt.clientExists())
        #print(srvr.serverExists())
        #*dealing cards
        if not clnt.clientExists() or srvr.serverExists(): #either not a client (singleplayer) or the server
            #self.cardData = {'Hand':[], 'name':player.name} #dictionary for server (if needed)
            #self.cardData['Hand'] = {}
            self.cardData['Hand'][player.name] = []
            for i in range(0,amount):
                index = random.randint(0, len(self.cards)-1) #choosing a random card
                player.hand.append(self.cards[index]) #adding random card to location
                self.cardData["Hand"][player.name].append([self.cards[index].value, self.cards[index].suit])
                self.used.append(self.cards.pop(index)) #removing card and adding to used

                #*displaying card
                if type(player) is User: #users hand should be displayerd
                    player.hand[-1].enlarge(xCoOrd, yCoOrd+75)
                else: #opponents hands should remain hidden
                    player.hand[-1].flip(xCoOrd, yCoOrd+50)
                xCoOrd+=50

    def dealCommunity(self):
        dealSingleSound.play()
        #*Changing variables depending on current stage
        if ROUND.stage == "Flop":
            amount = 3
            xCoOrd = 785
        elif ROUND.stage == "Turn":
            amount = 1
            xCoOrd = 1055 
        elif ROUND.stage == "River":
            amount = 1
            xCoOrd = 1145
        yCoOrd = 490
        
        #*dealing cards
        if not clnt.clientExists() or srvr.serverExists(): #either not a client (singleplayer) or the server
            #cardData = {'Community':[]} #dictionary for server (if needed)
            #self.cardData['Community'] = {}

            for i in range(0, amount):
                index = random.randint(0, len(self.cards)-1) #choosing a random card
                ROUND.community.append(self.cards[index]) #adding random card to location
                self.cardData['Community'].append([self.cards[index].value, self.cards[index].suit])
                self.used.append(self.cards.pop(index)) #removing card and adding to used
                ROUND.community[-1].place(xCoOrd, yCoOrd) #displaying card
                xCoOrd+=90

            '''if srvr.serverExists(): #need to send the cards to clients
                cardData = str(cardData)
                clnt.sendMessage(cardData.encode(FORMAT))'''

    def clientDealPlayer(self, allCards, name):
        toBeRemoved = []
        for player in allPlayers:
            if player.name == name:
                xCoOrd = player.x - 25
                yCoOrd = player.y
                for card in self.cards:
                    if [card.value, card.suit] in allCards:
                        player.hand.append(card) #adding card to location
                        toBeRemoved.append(card) #indicating card needs removal

                        #*displaying card
                        if type(player) is User: #users hand should be displayed
                            player.hand[-1].enlarge(xCoOrd, yCoOrd+75)
                        else: #opponents hands should remain hidden
                            player.hand[-1].flip(xCoOrd, yCoOrd+50)
                        xCoOrd+=50

        for card in toBeRemoved: #removing cards
            index = self.cards.index(card)
            self.used.append(self.cards.pop(index)) #adding to used     

    def clientDealCommunity(self, allCards):
        #*Changing variables depending on current stage
        if len(ROUND.community) == 0: #DEAL FLOP
            xCoOrd = 785
        elif len(ROUND.community) == 3: #DEAL TURN
            xCoOrd = 1055 
        elif len(ROUND.community) == 4: #DEAL RIVER
            xCoOrd = 1145
        yCoOrd = 490
        
        #*Adding each card the client has been sent to the community cards
        toBeRemoved = []
        for card in self.cards:
            if [card.value, card.suit] in allCards:
                ROUND.community.append(card) #adding card to location
                toBeRemoved.append(card) #indicating card needs removal
                ROUND.community[-1].place(xCoOrd, yCoOrd) #displaying card
                xCoOrd+=90
            
        for card in toBeRemoved: #removing cards
            index = self.cards.index(card)
            self.used.append(self.cards.pop(index)) #adding to used
 
    def sendCardData(self):
        if srvr.serverExists(): #need to send the cards to clients
            cardData = str(self.cardData)
            clnt.sendMessage(cardData.encode(FORMAT))
            #self.cardData['Hand'] = {}
            self.cardData = {'Hand': {}, 'Community': []}

class Round(object):
    def __init__(self):
        self.community = []
        self.pot = 0
        self.stage = STAGES[0]
        self.bigBlind = 10
        self.currPlayer = 1
        self.currBet = 0
        self.allIn = False
        self.timerHide = False

        #*Pot
        self.potImage = ImageTk.PhotoImage(Image.open("../Entities/Chips/potChips.png"))
        self.physPot = canvas.create_image(850, 360, image=self.potImage, anchor=tk.NW)

        self.potLabel = canvas.create_text(940, 390, text="$"+str(self.pot), font=(FONTNAME,30), fill="#00FFFF")

    def nextStage(self):
        collectPotSound.play()
        print("[NEXT STAGE] Current: " + str(self.stage))
        newRound = False
        #*incrementing stage
        try:
            self.stage = STAGES[STAGES.index(self.stage)+1]
        except: #reached the final stage
            self.stage = STAGES[0] #set stage to first stage
            newRound = True

        #preparing each player for next stage
        for player in allPlayers:
            if player.position == "BTN":
                self.currPlayer = player.index #setting the action to BTN player
            if not player.folded: #if player still in round
                player.ready = False
                player.currBet = 0
                if type(player) is User:
                    player.preSelect.enable(canvas, 2) #enabling check button

            player.unplaceIcon()

        #print("[NEXT STAGE] Next: "+str(self.stage))
        #automatically dealing community cards
        if self.stage in ["Flop","Turn","River"]:
            DECK.dealCommunity()
        
        if srvr.serverExists():
            DECK.sendCardData()

        self.currBet = 0
        
        if newRound:
            allPlayers[self.currPlayer].pauseTurn()
            self.showdown() #initiate a the showdown
        else:
            self.nextPlayer(self.currPlayer) #finding the next player to start the round

    def showdown(self):
        winnerIndex = self.calcWinner()
        allPlayers[self.currPlayer].pauseTurn() #pauses the current players turn
        if isinstance(winnerIndex, int): #single winner
            winner = allPlayers[winnerIndex] #find which player has won
            winner.balance += self.pot #giving pot to them
            winnerDraw, winnerRank = winner.bestRank(self.community)
            bannerText = f"Winner is {winner.name} With a {winnerRank}\n Wins a Pot of {self.pot}"
            #*updating widgets
            canvas.itemconfigure(winner.balanceLabel, text="$"+str(winner.balance))
        else: #multiple winners
            bannerText = "Winners Are: "
            for index in winnerIndex:
                winner = allPlayers[index]
                winner.balance += self.pot//len(winnerIndex) #dividing pot equally
                winnerDraw, winnerRank = winner.bestRank(self.community)
                bannerText = bannerText + winner.name + ", " #adding list of names to banner text
                canvas.itemconfigure(winner.balanceLabel, text="$"+str(winner.balance)) #*updating widgets
            bannerText = bannerText + "\nWith a " + winnerRank + " Divide a Pot of " + str(self.pot) #adding extra info to text

        #*Creating banner to display the winner
        self.bannerImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/newBanner2.png"))
        self.winnerBanner = canvas.create_image(480, 430, image=self.bannerImage, anchor=tk.NW, tags="banner")
        self.winnerText = canvas.create_text(1030, 600, text=bannerText, 
                            font=(BOLDFONT,25), fill = "white", tags="banner",justify=CENTER)

        #*Revealing all players cards
        for player in allPlayers:
            for card in player.hand:
                card.reveal()

        canvas.after(10000, self.deleteBanner)
        
    def newRound(self):
        print("[NEW ROUND]")
        shuffleSound.play()

        print(DECK.used)
        #resetting deck
        for card in DECK.used:
            DECK.cards.append(card)

        print(DECK.cards)
        #removing cards from GUI
        for card in DECK.cards:
            card.unplace()

        #resetting variables
        DECK.used = []
        self.community = []
        self.currBet = 0
        self.pot = 0
        self.allIn = False
        self.stage = STAGES[0]

        #finding the player with the button
        for player in allPlayers:
            if player.position == "BTN":
                btnIndex = player.index
                player.position = allPositions[-1]

        #Giving button to next available player
        for i in range(btnIndex+1, btnIndex+len(allPlayers)-1):
            try: #Index erorr
                ##print(f"Player {i} has a balance of {allPlayers[i].balance}")
                if allPlayers[i].balance > 0 :
                    allPlayers[i].position = "BTN"
                    #print(str(allPlayers[i].name)+" received the BTN")
                    break
            except:
                ##print(f"Player {i-len(allPlayers)} has a balance of {allPlayers[i-len(allPlayers)].balance}")
                if allPlayers[i-len(allPlayers)].balance > 0:
                    allPlayers[i-len(allPlayers)].position = "BTN"
                    #print(str(allPlayers[i-len(allPlayers)].name)+" received the BTN")
                    break
        ##print(allPlayers)

        if len(allPlayers) == 2: #heads up
            newBtnIndex = int(not btnIndex) #1 goes to 0 and 0 goes to 1

        #*Eliminating any players
        toBeElim = []
        for player in allPlayers:
            #print(f"Player {player.name} balance of {str(player.balance)}")
            if player.balance <= 0:
                toBeElim.append(player)
        for player in toBeElim:
                player.eliminatePlayer()

        #if one player left
        if len(allPlayers) == 1:
            endGame(allPlayers[0].name)
            return

        #*Updating indexes
        for player in allPlayers:
            player.updateIndex(allPlayers.index(player))
            #player.index = allPlayers.index(player)

        #finding the player with the button after removing players
        for player in allPlayers:
            if player.position == "BTN":
                newBtnIndex = player.index
                #print(player.position)

        #print("[NEW ROUND] "+str(allPositions)+", OLD BTN: "+str(btnIndex)+", NEW BTN: "+str(newBtnIndex))
        ##print(allPlayers)
        #incrementing positions
        for player in allPlayers: #incrementing their position
            difference = player.index - newBtnIndex
            print("Next index: "+str(difference)+", Current: "+str(player.position))
            player.position = allPositions[difference]
            print("New: "+player.position)

        #preparing for new round
        for player in allPlayers:
            #resetting player attributes
            player.hand = []
            player.ready = False
            player.allIn = False
            player.currBet = 0
            player.folded = False
            player.unplaceIcon()
            DECK.dealPlayer(2, player)

            #automatically dealing blinds and setting current position
            if player.position == "SB":
                player.placeSB()
                if len(allPlayers) == 2:
                    self.currPlayer = player.index
            elif player.position == "BB":
                player.placeBB()
            elif player.position == "UTG":
                self.currPlayer = player.index
            elif player.position == "BTN":
                if len(allPlayers) == 2: #2 players left
                    player.placeBB()
                if len(allPlayers) == 3: #exactly 3 players left
                    self.currPlayer = player.index

            #*updating widgets
            canvas.itemconfigure(player.posLabel, text=player.position)
            canvas.itemconfigure(player.block, outline=player.colour)
            if type(player) is User:
                player.preSelect.place(canvas)
                canvas.itemconfigure(player.block, outline=PRIMARYCOLOUR)
        allPlayers[self.currPlayer].currTurn()
        DECK.sendCardData()

    def nextPlayer(self, index):
        ##print("[NEXT PLAYER] Current: "+str(index))
        player = allPlayers[index]

        #*Validating the player's timer has been removed
        try:
            player.timer.destroy()
            ##print(f"[NEXT PLAYER] Timer found for player {index}")
        except:
            pass
            ##print(f"[NEXT PLAYER] Timer not found for player {index}")

        if self.numPlayersLeft():
            self.dealRest()
            return #breaks out of function

        #*finding the next player who has not folded
        while True:
            #*looping to the next player
            index+=1
            try:
                player = allPlayers[index]
            except:
                player = allPlayers[0]
                index = 0
            
            if not player.folded and not player.allIn: #if the player has not folded
                break

        ##print("[NEXT PLAYER] Found: "+str(index))
        #*checking to see if we need to move to the next stage
        if player.ready:
            self.nextStage()
        else:
            self.currPlayer = index
            player.currTurn()
            
    def updatePot(self, amount):
        self.pot += amount #updating pot
        #*updating widgets
        canvas.itemconfigure(self.potLabel, text="$"+str(self.pot))

    def calcWinner(self):
        winnerRank = -1
        #for each player who has not folded
        for player in allPlayers:
            if not player.folded:
                bestHand, rankName = player.bestRank(self.community) #calculate their best hand
                rankValue = RANKS[rankName]
                #print("[PLAYER INDEX] " + str(player.index))
                #print("[BEST HAND] " + str(bestHand))
                #print("[BEST RANK] " + rankName)
                if rankValue > winnerRank: #comparing rank to previous best
                    winnerRank = rankValue #setting previous to current rank
                    index = player.index
                elif rankValue == winnerRank:
                    try: #already people with same rank
                        index.append(player.index) #add their index to list of winner indexes
                    except:
                        index = [index, player.index] #create list of winner indexes

                #print("[WINNNER INDEX] "+str(index))
        
        #*Checking if there are multiple players with same rank
        if isinstance(index, list): #multiple winenrs
            index = self.valueCompare(index)

        return index

    def valueCompare(self, allIndexes):
        allHands = []
        #ALL HANDS IS A 2D ARRAY, EACH ELEMENT COSISTS OF AN ARRAY OF 6 ELEMENTS
        #FIRST 5 ELEMENTS ARE VALUES OF BEST HAND IN DESC ORDER, LAST ELEMENT IS PLAYER INDEX
        for index in allIndexes:
            allHands.append([])
            #*adding value of every card in their best hand
            for card in allPlayers[index].bestRank(self.community)[0]:
                allHands[-1].append(card.value)
            allHands[-1].append(index) #adding index to the end

        winnerIndex = -1
        for _ in range(5):
            #print("[ALLHANDS] "+str(allHands))
            #*Comparing maximum values from each hand
            allMaxes = []
            #adding each hands max value to array
            for player in allHands:
                allMaxes.append(player[0]) 

            removal = [] #array of all hands to remove
            for i, each in enumerate(allMaxes):
                if each != max(allMaxes): #if it is lower than the max value
                    removal.append(allHands[i]) #add it to the removal list
                    
            for each in removal: #removing each hand in the removal list
                    allHands.remove(each) #remove the hand

            if len(allHands) == 1: #only one hand left
                winnerIndex = allHands[0][-1] #setting the winner to the owner of that hand
                break
            else:
                for player in allHands: #removing the highest value from each remaining hand
                    player.remove(player[0])
                    
        #*Two or more identical hands
        if winnerIndex == -1:
            winnerIndex = []
            #create an array of all the winners' indexes
            for each in allHands:
                winnerIndex.append(each[-1])

        #print(f"[VALUE COMPARE] {str(winnerIndex)}")
        return winnerIndex

    def deleteBanner(self):
        canvas.delete("banner") #deleting winner banner
        self.newRound() #initiating new round

    def numPlayersLeft(self):
        playerCount = 0
        allInCount = 0
        flag = False
        for player in allPlayers: #counting how many players are still active
            if not player.folded: #neither folded or all In
                playerCount += 1
            if player.allIn:
                allInCount += 1
        #print("[NUM PLAYERS] Remaining: "+str(playerCount)+", All In: "+str(allInCount))
        if (playerCount == 1): #only one player left
            flag = True
        elif (playerCount == allInCount): #all players are all in
            flag = True
        elif (allInCount == playerCount-1): #all but one players are all in
            #Checking if the one remaining player is ready
            for player in allPlayers:
                if not player.allIn and not player.folded:
                    if player.ready:
                        flag = True
        return flag

    def dealRest(self):
        amount = 0
        #*dealing remainder of community cards

        #determining how many times dealCommunity method will need to be called
        if self.stage == "Preflop":
            amount = 3
        elif self.stage == "Flop":
            amount = 2
        elif self.stage == "Turn":
            amount = 1

        for i in range(amount):
            self.stage = STAGES[STAGES.index(self.stage)+1]
            DECK.dealCommunity()

        if srvr.serverExists():
            DECK.sendCardData()
            ##print("[DEAL REST] Stage:"+str(self.stage)+", Commmunity: "+str(self.community))
        
        #if not clnt.clientExists() or srvr.serverExists(): #either the server or singleplayer
            
            
        canvas.after(1000, self.showdown)

class Tutor(object):
    def __init__(self, level, index):
        self.level = level #0-2 represent AI levels
        self.index = index

        #level 3 represents tutor used by user
        if self.level == 3:
            self.createIcons()

    def createIcons(self):
        self.headImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/Tutor/head.png"))
        self.head = canvas.create_image(1650, 25, image=self.headImage, anchor=tk.NW)

        extendFunc = partial(self.extend, canvas)
        self.expand = newButton(canvas, 1680, 290, "expand.png", "tutor", extendFunc)

        self.speechBubbleImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/Tutor/spBubble.fw.png"))
        self.tutorExtImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/Tutor/tutorExt.fw.png"))

        equityStyle = ttk.Style()
        equityStyle.theme_use('clam')
        equityStyle.configure("equity.Horizontal.TProgressbar", background="blue", troughcolor="black", foreground="black", 
            bordercolor="black", darkcolor="blue", lightcolor="blue")
        self.equityBar = ttk.Progressbar(canvas, orient=HORIZONTAL, length=120, mode="determinate", style="equity.Horizontal.TProgressbar")
        self.equityBar['value'] = 100
        self.equityBar.place(x=1715, y=210)

    def extend(self, canvas, event):
        buttonPressSound.play()

        #*Creating drop down extension
        self.tutorExt = canvas.create_image(1680, 300, image=self.tutorExtImage, anchor=tk.NW, tags="extension")

        #*Creating button to close extension
        exitFunc = partial(self.closeExtension, canvas)
        self.exitButton = newButton(canvas, 1680, 750, "exitTutor.fw.png", "extension", exitFunc)

        #*creating refresh button
        self.refreshButton = newButton(canvas, 1700, 320, "refresh.fw.png", "extension", self.refresh)
        self.extendText = ""
        self.extendLabel = canvas.create_text(1696, 390, text=self.extendText, fill=PRIMARYCOLOUR, font=(FONTNAME,15), anchor=tk.NW, tags="extension")
        self.refresh(None)
        
    def refresh(self, event):
        if ROUND.stage == "Turn" or ROUND.stage == "Flop" or ROUND.stage == "River":
            amCall = ROUND.currBet - allPlayers[self.index].currBet
            self.equity, self.outs = self.calcEquity(self.index, ROUND.stage)
            self.EV, self.potOdds = self.calcEV(amCall)
            self.rankProbs = self.eachRank(self.index)
            self.extendText = f"EV: {self.EV}\nNo. Outs: {self.outs}\nEquity: {self.equity}\n\n"
            self.bestRank = allPlayers[self.index].bestRank(ROUND.community)

            #adding rank stats to text
            for rank in self.rankProbs:
                text = rank + " : " + str(self.rankProbs[rank]) + "\n"
                self.extendText += text
            self.extendText += "\nRank: "+str(self.bestRank[1])

            if self.level == 3: #user - updating GUI
                canvas.itemconfigure(self.extendLabel, text=self.extendText)
                self.equityBar['value'] = self.equity
        elif ROUND.stage == "Preflop":
            amCall = ROUND.currBet - allPlayers[self.index].currBet
            self.PFScore, self.equity = self.preFlopCalc(self.index)
            self.EV, self.potOdds = self.calcEV(amCall)

            self.extendText = f"EV: {self.EV}\nPot Odds: {self.potOdds}:1\nEquity: {self.equity}%"
            if self.level == 3: #user - updating GUI
                canvas.itemconfigure(self.extendLabel, text=self.extendText)
                self.equityBar['value'] = self.equity

    def closeExtension(self, canvas, event):
        buttonPressSound.play()
        #*Closes extension
        canvas.delete("extension")

    def calcEV(self, amCall):
        potSize = ROUND.pot
        percentEquity = self.equity/100
        EV = ((potSize+amCall)*percentEquity) - amCall
        if amCall > 0: #avoiding division error
            potOdds = potSize/amCall
        else:
            potOdds = 0
            EV = 0

        EV = round(EV, 2)
        potOdds = round(potOdds, 2)
        return EV, potOdds

    def calcEquity(self, index, stage):
        outs = 0
        currRank = allPlayers[index].bestRank(ROUND.community)[1] #finding our best rank
        remainingCards = allPlayers[index].remCards() #finding the remaining cards

        #repeating for each remaining card
        for card in remainingCards:
            highestRank = allPlayers[index].bestRank(ROUND.community + [card])[1]
            if RANKS[highestRank] > RANKS[currRank]: #if the card gives us a better rank
                outs += 1

        #calculating equity
        if stage == "Flop":
            equity = (outs/47)
        elif stage == "Turn":
            equity = (outs/46)
        else:
            equity = 0
            outs = 0

        equity = round(equity*100, 2)
        return equity, outs

    def calcOuts(self, index, stage):
        #creating a dictionary for each rank with number of outs as the values

        rankOuts = {}
        for each in RANKS:
            rankOuts[each] = 0

        remainingCards = allPlayers[index].remCards() #finding the remaining cards
        if stage == "Flop":
            copyDeck = remainingCards[:]
            for card in remainingCards:
                turnCard = copyDeck.pop(copyDeck.index(card))
                for riverCard in copyDeck:
                    #finding the best rank including the two new cards we have added
                    highestRank = allPlayers[index].bestRank(ROUND.community + [turnCard, riverCard])[1]
                    rankOuts[highestRank] += 1
                copyDeck.append(turnCard)
        elif stage == "Turn":
            for riverCard in remainingCards:
                #finding best rank including new card we added
                highestRank = allPlayers[index].bestRank(ROUND.community + [riverCard])[1]
                rankOuts[highestRank] += 1 #adding an out to whichever rank we found
        return rankOuts

    def eachRank(self, index):
        rankProbs = {}
        if ROUND.stage == "Flop":
            rankOuts = self.calcOuts(index, "Flop") #calc outs for each rank

            #calculating probability for each rank
            for each in rankOuts:
                probability = (rankOuts[each]/2162)*100
                probability = round(probability, 2)
                rankProbs[each] = probability
        elif ROUND.stage == "Turn":
            rankOuts = self.calcOuts(index, "Turn") #calc outs for each rank

            #calculating the probability for each rank
            for each in rankOuts:
                probability = (rankOuts[each]/46)*100
                probability = round(probability, 2)
                rankProbs[each] = probability
        elif ROUND.stage == "River":
            #the best rank has 100% probaility on the river the other ranks have 0
            for each in RANKS:
                rankProbs[each] = 0
            highestRank = allPlayers[index].bestRank(ROUND.community)[1]
            rankProbs[highestRank] = 100
        return rankProbs

    def preFlopCalc(self, index):
        #equity varies from 10 - 66
        #score varies from 7 - 42
        hand = allPlayers[index].hand
        card1 = hand[0]
        card2 = hand[1]
        score = card2.value + card1.value #adding values to score
        equity = card1.value + card2.value + 10
        if card1.value == card2.value: #if values are same
            score += card1.value
            equity += (card1.value)*2
        elif card1.suit == card2.suit: #suited
            score += max([card1.value, card2.value])
            equity += 3

        if abs(card1.value - card2.value) == 1: #connector
            score += 3
        elif abs(card1.value - card2.value) == 2: #2 seperaation
            score += 1
        elif abs(card1.value - card2.value) >= 5: #gap of 5 or more
            score -= (abs(card1.value - card2.value))//2

        equity -= abs(card1.value - card2.value)
        return score, equity

    def suggestMove(self, move):
        #*creates a speech bubble to suggest a move
        self.speechBubble = canvas.create_image(1500, 15, image=self.speechBubbleImage, anchor=tk.NW, tags="speech")
        self.speechText = canvas.create_text(1525, 20, text="The PokerTutor\nsuggests you should\n "+move, 
            font=(FONTNAME, 16), fill=PRIMARYCOLOUR, justify=CENTER, tags="speech", anchor=tk.NW)
        canvas.after(10000, self.deleteSpeech)

    def deleteSpeech(self):
        canvas.delete("speech") #deletes the speech bubble and text

    def optimalMove(self):
        self.refresh(None)
        if self.level == 0:
            move = self.easyMove()
        elif self.level == 1:
            move = self.proMove()
        elif self.level >= 2:
            move = self.expertMove()
        return move

    def easyMove(self):
        player = allPlayers[self.index]
        amCall = ROUND.currBet - player.currBet

        if ROUND.stage == "Preflop":
            if amCall >= player.balance//2:
                move = "FOLD"
            else:
                move = "CALL"
        else: #FLOP/TURN/RIVER
            rankValue = RANKS[self.bestRank[1]] #best rank
            if rankValue >= 4:
                if amCall >= player.balance//2:
                    move = "CALL"
                else:
                    if ROUND.stage == "River":
                        move = "ALLIN"
                    else: #TURN/RIVER
                        move = "HALFRAISE"
            elif rankValue >= 2:
                if amCall <= player.balance//2:
                    move = "CALL"
                else:
                    move = "MINRAISE"
            else:
                if ROUND.currBet == 0:
                    move = "CHECK"
                else:
                    move = "FOLD"
        return move
    
    def proMove(self):
        player = allPlayers[self.index]
        amCall = ROUND.currBet - player.currBet

        if ROUND.stage == "Preflop":
            if self.PFScore >= 40: #amazing hand
                move = "ALLIN"
            elif self.PFScore >= 25: #good hand
                if self.EV >= 2 and self.potOdds >= 3:
                    move = "MINRAISE"
                elif amCall <= player.balance//4:
                    move = "CALL"
                else:
                    move = "FOLD"
            elif self.PFScore >= 15: #mediocre hand
                if amCall <= player.balance//4:
                    move = "CALL"
                else:
                    move = "FOLD"
            else:
                move = "FOLD"
        else: #FLOP/TURN/RIVER
            rankValue = RANKS[self.bestRank[1]]
            if rankValue >= 4:
                if ROUND.currBet == 0:
                    raiseEV, raisePotOdds = self.calcEV(ROUND.bigBlind)
                else:    
                    raiseEV, raisePotOdds = self.calcEV(ROUND.currBet*2)
                if raiseEV >= 0: #TODO 
                    if ROUND.stage == "River":
                        if raisePotOdds >= 5:
                            move = "ALLIN"
                        else:
                            move = "HALFRAISE"
                    else:
                        move = "MINRAISE"
                elif self.equity >= 30:
                    move = "MINRAISE"
                else:
                   move = "CALL"
            elif rankValue >= 2:
                if self.EV >= 0 and self.potOdds >= 2:
                    if amCall <= player.balance//4:
                        move = "MINRAISE"
                    else:
                        move = "CALL"
                else:
                    if self.equity >= 50:
                        move = "HALFRAISE"
                    elif self.equity >= 30:
                        move = "MINRAISE"
                    elif amCall <= player.balance//2:
                        move = "CALL"
                    else:
                        move = "FOLD"
            else:
                if ROUND.currBet == 0:
                    if ROUND.stage == "RIVER" and self.calcEV(ROUND.bigBlind)[0] >= 0 :
                        move = "MINRAISE"
                    else:
                        if self.equity >= 50:
                            move = "MINRAISE"
                        else:
                            move = "CHECK"
                else:
                    move = "FOLD"
        return move
                    
    def expertMove(self):
        move = self.proMove()
        '''moveScore = 0
        moveScore += self.EV
        if ROUND.stage == "Turn" or ROUND.stage == "Flop" or ROUND.stage == "River":
            moveScore += (RANKS[self.bestRank])*5
            if allPlayers[self.index].position in ["BTN", "CO"]: #late positions
                moveScore + 20
            elif allPlayers[self.index].position in ["LJ","HJ", "MP+1"]: #middle positions
                moveScore += 5
            elif allPlayers[self.index].position in ["SB","BB", "UTG"]: #early positions
                moveScore -= 5'''
        return move

#!subprograms
def openNewGame(window, event):
    buttonPressSound.play()
    canvas.destroy()
    srvr.closeServer()
    
    titleScreen.runTitleScreen(window)
    
    #closing server if multiplayer game
    #if getJson("Settings.json",("options","GameType")) == "MULTI":
    

    exit()

def closePopUp(event):
    #*STAY button pressed on pop up
    buttonPressSound.play() #playing button press sound
    canvas.delete("popUp") #deleting pop up

def ingameSettings(event):
    global inGameBgImage, inGameCanvas, exitSettingsButton, saveButton, listb, saveLabel
    global muteButton, fullScreenButton, unMuteButton, gameCodeLabel, AILevelButton

    buttonPressSound.play()
    inGameCanvas = tk.Canvas(canvas, width=1516, height=816, borderwidth=0) #creating background for settings
    inGameCanvas.place(x=210, y=140)

    ROUND.timerHide = True #timers showuld be hidden
    allPlayers[ROUND.currPlayer].hideTimer() #hiding the current players timer

    inGameBgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/inGameBack.fw.png")) 
    inGameBg = inGameCanvas.create_image(0, 0, image=inGameBgImage, tags="inGame", anchor=tk.NW) #background image for settings

    exitSettingsButton = newButton(inGameCanvas, 30, 30, "settingsExit.fw.png", "inGame", exitSettings) #exit button

    #*mute and unmute button
    muteButton = newButton(inGameCanvas, 300, 300, "tealButton.fw.png", "inGame", muteFunc)
    muteButton.addLabel(inGameCanvas, "MUTE", "white", (440, 350), 30, "inGame", muteFunc)

    unMuteButton = newButton(inGameCanvas, 600, 300, "tealButton.fw.png", "inGame", unMuteFunc)
    unMuteButton.addLabel(inGameCanvas, "UNMUTE", "white", (740, 350), 30, "inGame", unMuteFunc)

    if getJson("Settings.json", ("options", "GameType")) == "SINGLE":
        #*Creating listbox with all save files
        listb = tk.Listbox(inGameCanvas, bg="grey", fg="white", width=40, height=5, font=(FONTNAME,25), bd=0, justify=CENTER,
        selectforeground=SECONDARYCOLOUR, selectbackground="white")
        for file in os.listdir("Saves/"): #repeating through every save file
            file = file.replace(".json","")
            listb.insert(tk.END, file)
        listb.place(x=200,y=500)

        saveButton = newButton(inGameCanvas, 1100, 530, "tealButton.fw.png", "inGame", saveGame) #button to save game
        saveButton.addLabel(inGameCanvas, "SAVE", "white", (1240, 580), 30, "inGame", saveGame)
        saveLabel = inGameCanvas.create_text(800, 740, text="", font=(FONTNAME,30), fill="white")
    else:
        gameCodeLabel = inGameCanvas.create_text(300, 100, text="Game code is: ", font=FONTNAME, fill="white")

def saveGame(event):
    buttonPressSound.play()
    #validation
    if listb.get(ANCHOR) == "":
        inGameCanvas.itemconfigure(saveLabel, text="Save name must not be empty")
    else:
        jsonData = {}
        jsonData["allPlayers"] = []
        for player in allPlayers:
            jsonData["allPlayers"].append({})
            jsonData["allPlayers"][-1]["name"] = player.name
            jsonData["allPlayers"][-1]["balance"] = player.balance
            jsonData["allPlayers"][-1]["position"] = player.position
            if player.index == THEUSER.index:
                jsonData["allPlayers"][-1]["user"] = True
            else:
                jsonData["allPlayers"][-1]["user"] = False
        jsonData["Gameplay"] = {}
        jsonData["Gameplay"]["maxPlayers"] = maxPlayers
        jsonData["Gameplay"]["levelAI"] = getJson("Settings.json", ("options", "AI Level"))
        jsonData["Gameplay"]["Tutor"] = getJson("Settings.json", ("settings","Tutor"))
        writeJson("Saves/", listb.get(ANCHOR), jsonData)
        inGameCanvas.itemconfigure(saveLabel, text="Saved to "+listb.get(ANCHOR))

def playerInfo():
    jsonData = {}
    jsonData["allPlayers"] = []
    for player in allPlayers:
        jsonData["allPlayers"].append({})
        jsonData["allPlayers"][-1]["name"] = player.name
        jsonData["allPlayers"][-1]["position"] = player.position
    jsonData["Gameplay"] = {}
    jsonData["Gameplay"]["maxPlayers"] = maxPlayers
    jsonData["Gameplay"]["startStack"] = startStack
    jsonData["Gameplay"]["Assists"] = assistsAllowed

    return jsonData

def exitSettings(event):
    inGameCanvas.destroy() #destroying settings canvas and widgets
    ROUND.timerHide = False #timers should be displayed
    allPlayers[ROUND.currPlayer].createTimer() #creating current players timer

def endGame(winnerName):
    global endPopUp, leaveBtn
    endPopUp = newPopUp(canvas, f"Congratulations to {winnerName}\n for winning!")

    #*Creating buttons
    leaveBtn = newButton(canvas, 500, 660, "redButton.fw.png", "popUp", closePopUp)
    leaveBtn.addLabel(canvas, "LEAVE", "white", (615, 700), 30, "popUp", closePopUp)

def createGameplay(window):
    global canvas, startStack, texturePack, allPlayers, allCoOrds, allPositions, potLabel, assistsAllowed
    global DECK, ROUND, bgImage, tableImage, deckImage, exitButton, settingsButton

    allPositions = []
    allCoOrds = []
    allPlayers = []

    print("Running gameplay...")
    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.pack()

    settings = readJson("Settings.json")
    startStack = (settings["options"]["StartStack"])*10
    numPlayers = int(settings["options"]["MaxPlayer"])
    assistsAllowed = settings["options"]["Assists"]
    
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

    settingsButton = newButton(canvas, 60, 220, "settingsCog.png", None, ingameSettings)

    #*Creating deck of cards
    DECK = Deck()

    for suit in SUITS:
        for value in VALUES:
            DECK.cards.append(Card(suit, value))

    #*starting round
    ROUND = Round()

def runGameplay(window):
    global allPlayers, allPositions, allCoOrds, THEUSER, maxPlayers

    createGameplay(window)

    #*getting number of players
    maxPlayers = int(getJson("Settings.json", ("options","MaxPlayer")))
    if maxPlayers == 9: #changing variable to fit with number of players
        allPositions = MAX9[:]
        allCoOrds = NINECOORDS[:]
    elif maxPlayers == 6:
        allPositions = MAX6[:]
        allCoOrds = SIXCOORDS[:]

    name = getJson("Settings.json",("settings","Name"))

    #*creating player object
    for i in range(0,maxPlayers):
        if i == 0:
            allPlayers.append(User(name, allPositions[i], i, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
            THEUSER = allPlayers[-1]
        else:
            allPlayers.append(AI(NAMES[i], allPositions[i], i, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
        allPlayers[-1].createBlock()

    dealSound.play()
    for player in allPlayers:
        DECK.dealPlayer(2, player)

    for player in allPlayers:
        #automatically dealing blinds and setting current position
        if player.position == "SB":
            player.placeSB()
        elif player.position == "BB":
            player.placeBB()
        elif player.position == "UTG":
            ROUND.currPlayer = player.index
            player.currTurn()
        
    window.mainloop()

def loadGameplay(window, fileName):
    global allPlayers, allPositions, allCoOrds, maxPlayers, THEUSER

    createGameplay(window)
    path = "Saves/"+fileName+".json"
    jsonData = readJson(path)
    thePlayers = jsonData["allPlayers"]
    gameplayDict = jsonData["Gameplay"]

    #*getting number of players
    maxPlayers = int(gameplayDict["maxPlayers"])
    if maxPlayers == 9: #changing variable to fit with number of players
        allPositions = MAX9[:]
        allCoOrds = NINECOORDS[:]
    elif maxPlayers == 6:
        allPositions = MAX6[:]
        allCoOrds = SIXCOORDS[:]

    toRemove = maxPlayers - len(thePlayers) #amount of people eliminated

    #removing positions from allPositions array
    for i in range(toRemove):
        for pos in ORDERREMOVE:
            if pos in allPositions:
                allPositions.remove(pos)
                break

    #creating allPlayers array
    for i in range(0, len(thePlayers)):
        if thePlayers[i]["user"]:
            allPlayers.append(User(thePlayers[i]["name"], thePlayers[i]["position"], i, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
            allPlayers[-1].balance = thePlayers[i]["balance"]
            THEUSER = allPlayers[-1]
        else:
            allPlayers.append(AI(thePlayers[i]["name"], thePlayers[i]["position"], i, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
            allPlayers[-1].balance = thePlayers[i]["balance"]
        allPlayers[-1].createBlock()

    #automatically dealing blinds and setting current position
    for player in allPlayers:
        if player.position == "SB":
            player.placeSB()
            if len(allPlayers) == 2:
                ROUND.currPlayer = player.index
                player.currTurn()
        elif player.position == "BB":
            player.placeBB()
        elif player.position == "UTG":
            ROUND.currPlayer = player.index
            player.currTurn()
        elif player.position == "BTN":
            if len(allPlayers) == 2: #2 players left
                player.placeBB()
            if len(allPlayers) == 3: #exactly 3 players left
                ROUND.currPlayer = player.index
                player.currTurn()

    dealSound.play()
    for player in allPlayers:
        DECK.dealPlayer(2, player)

    window.mainloop()

def joinGameplay(window):
    createGameplay(window)

    clnt.sendMessage("READY".encode(FORMAT))

def decodeMessage(message):
    global THEUSER, maxPlayers, allPlayers, allCoOrds, allPositions, nextCreateIndex, assistsAllowed
    global reasonLeavePopUp, reasonPopUp
    #message is a dictionary describing what to do next

    for each in message:
        if each == "allPlayers": #new client!
            flag = True #can continue with joining server or not
            name = getJson("Settings.json", ("settings","Name"))
            maxPlayers = message['Gameplay']['maxPlayers']
            startStack = message['Gameplay']['startStack']
            assistsAllowed = message['Gameplay']['Assists']
            if len(message[each]) >= maxPlayers: #max players not reached
                flag = False
                reason = "Sorry! Game is full"
            else:
                for player in message[each]:
                    if player['name'] == name:
                        flag = False
                        reason = "Same name as another player!\n Change it in the settings menu."

            if flag:
                if maxPlayers == 9: #changing variable to fit with number of players
                    allPositions = MAX9[:]
                    allCoOrds = NINECOORDS[:]
                elif maxPlayers == 6:
                    allPositions = MAX6[:]
                    allCoOrds = SIXCOORDS[:]

                for i in range(-len(message[each]), 1):
                    index = i + len(message[each])
                    #index - index in allPlayers array
                    #i - index of colours/co ordinates
                    if i == 0:
                        #*creating user
                        name = getJson("Settings.json",("settings","Name"))
                        position = allPositions[index]
                        allPlayers.append(User(name, position, index, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
                        allPlayers[-1].balance = startStack
                        THEUSER = allPlayers[-1]

                        #*sending server our details
                        ourDetails = str({'Join': {'name': name, 'position': allPositions[index]} })
                        clnt.sendMessage(ourDetails.encode(FORMAT)) 
                    else:
                        #*Creating other players
                        position = message[each][index]['position']
                        name = message[each][index]['name']
                        allPlayers.append(multiPlayer(name, position, index, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
                        allPlayers[-1].balance = startStack
                    allPlayers[-1].createBlock()
                    
                nextCreateIndex = 1
            else:
                reasonPopUp = newPopUp(canvas, reason)

                reasonLeavePopUp = newButton(canvas, 500, 660, "redButton.fw.png", "popUp", closePopUp)
                reasonLeavePopUp.addLabel(canvas, "LEAVE", "white", (615, 700), 30, "popUp", closePopUp)
        elif each == "Join":
            #*Creating the player who just joined
            name = message[each]['name']
            position = message[each]['position']
            index = nextCreateIndex
            physicalIndex = len(allPlayers)
            allPlayers.append(multiPlayer(name, position, physicalIndex, COLOURS[index], allCoOrds[index][0], allCoOrds[index][1]))
            allPlayers[-1].createBlock()
            nextCreateIndex += 1
        elif each == "Move":
            name = message[each]['name']
            #*Finding the player who played the move
            for player in allPlayers:
                if player.name == name:
                    move = message[each]['move']
                    #*Playing the move
                    if move == "FOLD":
                        player.fold(None)
                    elif move == "CALL":
                        player.call(None)
                    elif move == "RAISE":
                        amount = message[each]['amount']
                        player.betRaise(amount, None)
                    elif move == "CHECK":
                        player.check(None)
        elif each == "Hand":
            cardDict = message[each]
            if cardDict != {}: #validation
                for name in cardDict:
                    playerHand = cardDict[name]
                    DECK.clientDealPlayer(playerHand, name)
        elif each == "Community":
            allCards = message[each]
            if allCards != []: #validation
                DECK.clientDealCommunity(allCards)
        elif each == "Start":
            startMulti(None)

def startMulti(event):
    global shortagePlayersPopUp, leaveShortageBtn, allPlayers, allPositions
    if len(allPlayers) >= 2:
        #sending start to clients
        if srvr.serverExists(): #host client
            startData = str({"Start":None})
            clnt.sendMessage(startData.encode(FORMAT))
            canvas.delete("startGame")
        
        #*removing positions from the allPosition array
        for pos in ORDERREMOVE:
            if pos in allPositions:
                allPositions.remove(pos)
                #*repeat until number of positions matches number of playerss
                if len(allPlayers) == len(allPositions):
                    break #stop removing position
            
        for player in allPlayers:
            #automatically dealing blinds and setting current position
            if player.position == "SB":
                player.placeSB()
                if len(allPlayers) == 2:
                    ROUND.currPlayer = player.index
            elif player.position == "BB":
                player.placeBB()
            elif player.position == "UTG":
                ROUND.currPlayer = player.index
            elif player.position == "BTN":
                if len(allPlayers) == 2: #2 players left
                    player.placeBB()
                if len(allPlayers) == 3: #exactly 3 players left
                    ROUND.currPlayer = player.index
            DECK.dealPlayer(2, player)
        allPlayers[ROUND.currPlayer].currTurn()
        DECK.sendCardData()
    else:
        shortagePlayersPopUp = newPopUp(canvas, "Not enough players to start!")

        leaveShortageBtn = newButton(canvas, 500, 660, "greenButton.fw.png", "popUp", closePopUp)
        leaveShortageBtn.addLabel(canvas, "OK", "white", (615, 700), 30, "popUp", closePopUp)

def runMultiGameplay(window):
    global startGameBtn, nextCreateIndex, allPlayers, allPositions, allCoOrds, maxPlayers, assistsAllowed, THEUSER

    createGameplay(window)

    #*getting number of players
    maxPlayers = int(getJson("Settings.json", ("options","MaxPlayer")))
    assistsAllowed = getJson("Settings.json", ("options","Assists"))
    if maxPlayers == 9: #changing variable to fit with number of players
        allPositions = MAX9[:]
        allCoOrds = NINECOORDS[:]
    elif maxPlayers == 6:
        allPositions = MAX6[:]
        allCoOrds = SIXCOORDS[:]

    name = getJson("Settings.json",("settings","Name"))

    allPlayers.append(User("Ambar", allPositions[0], 0, COLOURS[0], allCoOrds[0][0], allCoOrds[0][1])) #TODO change'Ambar' to name
    allPlayers[0].createBlock()
    THEUSER = allPlayers[0]
    nextCreateIndex = 1 #index of where to create next player

    startGameBtn = newButton(canvas, 20, 420, "greenButton.fw.png", "startGame", startMulti)
    startGameBtn.addLabel(canvas, "START" ,"white", (130,460), 30, "startGame", startMulti)

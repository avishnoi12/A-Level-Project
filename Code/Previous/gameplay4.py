#Pocket Aces gameplay
#Date started 20/12/21
#Last edited 20/1/21

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

#! imports
import random
import threading
from tkinter import HORIZONTAL, ttk

from pygame import image
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
            self.endTurn()

    def betRaise(self, amount, event):
        if amount >= self.balance: #ALL IN
            self.ready = True
            self.currBet = self.balance
            self.updateBal(self.currBet)
            ROUND.currBet = self.balance
            ROUND.allIn = True
            self.allIn = True

            #*updating GUI
            self.placeIcon("raise") #TODO change to all in icon
            THEUSER.updatePreSelect()
            ROUND.numPlayersLeft()
            self.endTurn()
        elif amount == 0:
            self.check(None)
        elif amount >= ROUND.currBet * 2: #valid raise
            #*everyone who was ready is no longer ready
            for player in allPlayers:
                if player.balance != 0 and not player.folded: #still can play in this round
                    player.ready = False
            self.ready = True
            self.currBet = amount
            self.updateBal(amount)
            ROUND.currBet = amount

            #*updating GUI
            self.placeIcon("raise")
            THEUSER.updatePreSelect()
            self.endTurn()

    def call(self, event):
        amount = ROUND.currBet
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

            self.endTurn()

    def fold(self, event):
        self.ready = True
        self.currBet = 0
        self.folded = True
        
        #*updating GUI
        self.placeIcon("fold")
        for card in self.hand:
            card.unplace()
        
        #*checking if only one player left
        ROUND.numPlayersLeft()

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
        straight = self.hasStraight(totalCards) #do they have a straight
        if straight != []: # they have a straight
            #checking if they have a straight flush, flush or just a straight
            rank = self.hasStraightFlush(totalCards, straight)
        elif self.hasSameCard(totalCards, 3): #if they have AT LEAST a TOAK
            if self.hasSameCard(totalCards, 4) == "Exact": #EXACTLY  a FOAK
                rank =  "FourOfAKind"
            elif self.hasSameCard(totalCards, 2) == "Exact": #full house
                rank = "FullHouse"
            elif self.hasFlush(totalCards) != "": #if they have a flush
                rank = "Flush"
            else:
                rank = "ThreeOfAKind"
        elif self.hasFlush(totalCards) != "": #if they have a flush
            rank = "Flush"
        elif self.hasSameCard(totalCards, 2): #AT LEAST a pair
            if self.hasTwoPair(totalCards):
                rank = "TwoPair"
            else:
                rank = "Pair"
        else:
            rank = "HighCard"

        return rank

    def hasFlush(self, totalCards):
        suits = ["C","D","H","S"]
        flushIn = ""
        cardSuits = []

        #*creating an array of just suits
        for card in totalCards:
            cardSuits.append(card.suit)

        #*repeating for every suit
        for suit in suits:
            if cardSuits.count(suit) >= 5: #at least 5 cards of same suit
                flushIn = suit #then they have a flush in this suit

        return flushIn
            
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
                ofAKind = True
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
        suit = self.hasFlush(totalCards) #checking if they ahve a flush
        anwser = False
        count = 0

        #*if they do have a flush
        if suit != "":
            #checking if the straight and the flush coincide
            for card in totalCards:
                if card.value in straight and card.suit == suit:
                    count+=1
            
            #*Deciding which rank they have
            if count >= 5:
                answer = "StraightFlush"
            else:
                answer = "Flush"
        else: #did not have a flush
            answer = "Straight"
        
        return answer

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
        #*editing block
        canvas.itemconfigure(self.block, fill=PRIMARYCOLOUR, outline="white")
        canvas.itemconfigure(self.posLabel, fill="white")
        canvas.itemconfigure(self.balanceLabel, fill="white")

        self.timer = ttk.Progressbar(canvas, orient=HORIZONTAL, length=200, mode="determinate")
        if not ROUND.timerHide: #if ingame settings is not open
            self.createTimer()

    def createTimer(self):
        self.timer.place(x=self.x-100, y=self.y-40)

    def hideTimer(self):
        self.timer.place_forget()

    def endTurn(self):
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
        ROUND.currBet = self.currBet
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

    def unplaceIcon(self):
        canvas.delete(self.icon)
        canvas.itemconfigure(self.iconLabel, text="")

    def remCards(self):
        allCards = DECK.cards[:] + DECK.used[:] #full deck of 52 cards
        totalCards = self.hand[:] + ROUND.community[:]

        #removing the cards you see from the total deck
        for card in allCards:
            for each in totalCards:
                if card.suit == each.suit and card.value == each.value:
                    allCards.remove(card)
        return allCards

    def timerUpdate(self, count):
        try:
            self.timer['value'] += 10 #validating timer exists
        except:
            pass
        else:
            if count < 9: #if timer hasnt reached its limit
                canvas.after(1000, self.timerUpdate, count+1)
            else: #timer has reached its limit
                self.force() #force a move

    def bestHand(self):
        pass #TODO return list of 5 cards which is their bestcards

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
        self.posLabel = canvas.create_text(self.x, self.y+240, text=str(self.position), fill=PRIMARYCOLOUR, font=(FONTNAME,25))
        self.nameLabel = canvas.create_text(self.x, self.y+320, text=str(self.name), fill=self.colour, font=(BOLDFONT,35))
        
    def currTurn(self):#TODO
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
            self.raiseBtn = newButton(canvas, 60, 930, "Action/raise.fw.png", "actions", self.betRaise)
            self.checkBtn = newButton(canvas, 1300, 930, "Action/check.fw.png", "actions", self.check)
            self.callBtn = newButton(canvas, 370, 930, "Action/call.fw.png", "actions", self.call) 
            self.foldBtn = newButton(canvas, 1610, 930, "Action/fold.fw.png", "actions", self.fold)

            canvas.after(1000, self.timerUpdate, 0)
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

    def betRaise(self, event):
        amount = self.raiseSlider.get() #getting raise amount
        super().betRaise(amount, event)

    def fold(self, event):
        super().fold(event)
        self.preSelect.hide(canvas)

    def endTurn(self):
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

class AI(Player):
    def __init__(self, name, position, index, colour, x, y):
        super().__init__(name, position, index, colour, x, y)
        self.tutor = Tutor(1)
    
    def currTurn(self):
        super().currTurn()
        self.chooseMove()

    def endTurn(self):
        super().endTurn()
        ROUND.nextPlayer(self.index)
        
    def chooseMove(self):
        self.timerUpdate(0)
        num = random.randint(0,10) #intger that decides which move
        timeToMove = random.randint(1000, 9000) #how much time taken to move
        if num >=8:
            canvas.after(timeToMove, self.fold, None)
        elif num >=1:
            canvas.after(timeToMove,self.call,None)
        else:
            canvas.after(timeToMove, self.betRaise, ROUND.currBet*2, None)

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

    def reveal(self, canvas):
        self.img = Image.open("../Entities/Cards/Front Faces/"+self.name+".png") #changing image
        self.physImage = ImageTk.PhotoImage(self.img)
        canvas.itemconfigure(self.displayedCard, image=self.physImage) #displaying image

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
            xCoOrd = 1055
        elif ROUND.stage == "River":
            amount = 1
            xCoOrd = 1145
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
        self.allIn = False
        self.timerHide = False

        #*Pot
        self.potImage = ImageTk.PhotoImage(Image.open("../Entities/Chips/potChips.png"))
        self.physPot = canvas.create_image(850, 360, image=self.potImage, anchor=tk.NW)

        self.potLabel = canvas.create_text(940, 390, text="$"+str(self.pot), font=(FONTNAME,30), fill="#00FFFF")

    def nextStage(self):
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

        #automatically dealing community cards
        if ROUND.stage in ["Flop","Turn","River"]:
            DECK.dealCommunity()

        self.currBet = 0
        
        if newRound:
            self.showdown() #initiate a the showdown
        else:
            self.nextPlayer(self.currPlayer) #finding the next player to start the round

    def showdown(self): #TODO stop players turn
        winnerIndex = self.calcWinner()
        if isinstance(winnerIndex, int): #single winner
            winner = allPlayers[winnerIndex] #find which player has won
            winner.balance += self.pot #giving pot to them
            winnerRank = winner.bestRank(self.community)
            bannerText = f"WINNER IS {winner.name} WITH A {winnerRank}\n WINS A POT OF {self.pot}"
        else: #multiple winners
            bannerText = "WINNERS ARE: "
            for winner in winnerIndex:
                winner.balance += self.pot//len(winnerIndex) #dividing pot equally
                winnerRank = winner.bestRank(self.community)
                bannerText = bannerText + ", " + winner.name #adding list of names to banner text
            bannerText = bannerText + "WITH A " + winnerRank + "DIVIDE A POT OF " + str(self.pot) #adding extra info to text

        #*Creating banner to display the winner
        self.bannerImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/banner.fw.png"))
        self.winnerBanner = canvas.create_image(300, 520, image=self.bannerImage, anchor=tk.NW, tags="banner")
        self.winnerText = canvas.create_text(550, 520, text=bannerText, 
                            font=(BOLDFONT,35), fill = PRIMARYCOLOUR, tags="banner",justify=CENTER, anchor=tk.NW)

        #*Revealing all players cards
        for player in allPlayers:
            for card in player.hand:
                card.reveal(canvas)

        canvas.after(10000, self.deleteBanner)
        #*updating widgets
        canvas.itemconfigure(winner.balanceLabel, text="$"+str(winner.balance))
        
    def newRound(self):
        #resetting deck
        for card in DECK.used:
            DECK.cards.append(card)

        #removing cards from GUI
        for card in DECK.cards:
            card.unplace()

        #resetting variables
        DECK.used = []
        self.community = []
        self.currBet = 0
        self.pot = 0
        self.allIn = False

        #preparing for new round
        for player in allPlayers:
            #*incrementing each players position
            try:
                player.position = allPositions[allPositions.index(player.position)+1]
            except:
                player.position = allPositions[0]

            #resetting player attributes
            player.hand = []
            player.ready = False
            player.currBet = 0
            player.folded = False
            DECK.dealPlayer(2, player)

            #automatically dealing blinds and setting current position
            if player.position == "SB":
                player.placeSB()
            elif player.position == "BB":
                player.placeBB()
            elif player.position == "UTG":
                self.currPlayer = player.index

            #*updating widgets
            canvas.itemconfigure(player.posLabel, text=player.position)
            canvas.itemconfigure(player.block, outline=player.colour)
            if type(player) is User:
                player.preSelect.place(canvas)
                canvas.itemconfigure(player.block, outline=PRIMARYCOLOUR)
        allPlayers[self.currPlayer].currTurn()

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
            
            if not player.folded and not player.allIn: #if the player has not folded
                break

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
                rankName = player.bestRank(self.community) #calculate their best hand
                rankValue = RANKS[rankName]
                if rankValue > winnerRank: #comparing rank to previous best
                    winenrRank = rankValue #setting previous to current rank
                    index = player.index
                elif rankValue == winnerRank:
                    try: #already people with same rank
                        index.append(player.index) #add their index to list of winner indexes
                    except:
                        index = [index, player.index] #create list of winner indexes
        
        #*Checking if there are multiple players with same rank
        if isinstance(index, list): #multiple winenrs
            index = self.compareSameRank(index, winnerRank)

        return index

    def compareSameRank(self, allIndexes, winnerRank):
        #*Compares hand of the same rank to find the winner(s)
        if winnerRank == 0: #HIGH CARD
            index = self.totalCompare(allIndexes)
        elif winnerRank in [1,2,3,7]: #Pair/Two Pair/TOAK/FOAK
            index = self.ofAKindCompare(allIndexes, winnerRank)
        else: #5 card draw
            index = self.totalCompare(allIndexes)
        return index

    def totalCompare(self, allIndexes):
        #*Compares hands by adding their total value
        bestTotal = 0
        for each in allIndexes:
            newTotal = 0
            bestHand = allPlayers[each].bestHand() #5 winning cards
            for card in bestHand: #summing values of their hand
                newTotal += card.value
            
            if newTotal > bestTotal: #if they have the best total so far
                index = each
            elif newTotal == bestTotal: #equal totals
                try:
                    index.append(each) #if already 2 players with equal total
                except:
                    index = [index, each]
                
        return index

    def ofAKindCompare(self, allIndexes, winnerRank): #TODO finsih algo
        #*Compres hands by looking at their 'Of a Kind' value
        bestVal = 0
        for each in allIndexes:
            bestHand = allPlayers[each].bestHand()

            cardsValue = []
            for card in bestHand:
                cardsValue.append(card.value)

            for eachVal in cardsValue:
                if cardsValue.count(eachVal) >= 2:
                    if eachVal > bestVal:
                        index = each
                    elif eachVal == bestVal:
                        try:
                            if each not in index:
                                index.append(each)
                        except:
                            index = [index, each]
        return index

    def deleteBanner(self):
        canvas.delete("banner") #deleting winner banner
        self.newRound() #initiating new round

    def numPlayersLeft(self):
        playerCount = 0
        amount = 0
        for player in allPlayers: #counting how many players are still active
            if not player.folded and not player.allIn: #neither folded or all In
                playerCount += 1

        if playerCount == 1:
            if self.allIn == True: #a player has gone all in
                #*dealing remainder of community cards

                #determining how many times dealCommunity method will need to be called
                if self.stage == "Preflop":
                    amount = 3
                elif self.stage == "Flop":
                    amount = 2
                elif self.stage == "Turn":
                    amount = 1

                for i in range(amount):
                    DECK.dealCommunity()
                    self.stage = STAGES[STAGES.index(self.stage)+1]

                self.showdown()
            else: #no players have gone all in so only one player left
                self.showdown() #jump straight to showdown

class Tutor(object):
    def __init__(self, level):
        self.level = level #0-2 represent AI levels

        #level 3 represents tutor used by user
        if self.level == 3:
            self.createIcons()

    def createIcons(self):
        self.headImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/head.png"))
        self.head = canvas.create_image(1650, 25, image=self.headImage, anchor=tk.NW)

        extendFunc = partial(self.extend, canvas)
        self.expand = newButton(canvas, 1680, 290, "expand.png", "tutor", extendFunc)

    def extend(self, canvas, event):
        buttonPressSound.play()

        #*Creating drop down extension
        self.tutorExtImage = ImageTk.PhotoImage(Image.open("../Entities/Icons/tutorExt.fw.png"))
        self.tutorExt = canvas.create_image(1690, 300, image=self.tutorExtImage, anchor=tk.NW, tags="extension")

        #*Creating button to close extension
        exitFunc = partial(self.closeExtension, canvas)
        self.exitButton = newButton(canvas, 1690, 700, "exitTutor.fw.png", "extension", exitFunc)

        #*creating refresh button
        self.refreshButton = newButton(canvas, 1690, 300, "refresh.png", "extension", self.refresh)
        self.extendText = "Test text: \n This is a demo"
        self.extendLabel = canvas.create_text(1690, 390, text=self.extendText, fill=PRIMARYCOLOUR, font=(FONTNAME,15), anchor=tk.NW, tags="extension")
        #self.refresh()
        
    def refresh(self, event):
        if ROUND.stage == "Turn" or ROUND.stage == "Flop":
            self.equity, self.outs = self.calcEquity(THEUSER.index, ROUND.stage)
            self.EV, self.potOdds = self.calcEV(ROUND.pot, self.equity, ROUND.currBet)
            self.rankProbs = self.eachRank(THEUSER.index)

            #Creating array of rank texts to be displayed
            rankText = []
            for rank in self.rankProbs:
                text = rank + " : " + str(self.rankProbs[rank])
                rankText.append(text)

            self.extendText = f"EV: {self.EV}\nEquity: {self.equity}\nStr-Flush: {rankText[0]}\nFoaK: {rankText[1]}"
            canvas.itemconfigure(self.extendLabel, text=self.extendText)
        elif ROUND.stage == "River":
            #TODO
            pass
        elif ROUND.stage == "Preflop":
            pass
        #TODO

    def closeExtension(self, canvas, event):
        buttonPressSound.play()
        #*Closes extension
        canvas.delete("extension")

    def calcEV(self, potSize, equity, amCall):
        EV = ((potSize+amCall)*equity) - amCall
        potOdds = potSize/amCall
        return EV, potOdds

    def calcEquity(self, index, stage):
        outs = 0
        currRank = allPlayers[index].bestRank(ROUND.community) #finding our best rank
        remainingCards = allPlayers[index].remCards() #finding the remaining cards

        #repeating for each remaining card
        for card in remainingCards:
            highestRank = allPlayers[index].bestRank(ROUND.community + [card])
            if RANKS[highestRank] > RANKS[currRank]: #if the card gives us a better rank
                outs += 1

        #calculating equity
        if stage == "Flop":
            equity = (outs*(93-outs))/2162
        elif stage == "Turn":
            equity = (outs/46)
        else:
            equity = 0

        equity = (round(equity, 2))*100
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
                    highestRank = allPlayers[index].bestRank(ROUND.community + [turnCard, riverCard]) 
                    rankOuts[highestRank] += 1
                copyDeck.append(turnCard)
        elif stage == "Turn":
            for riverCard in remainingCards:
                #finding best rank including new card we added
                highestRank = allPlayers[index].bestRank(ROUND.community + [riverCard])
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
            highestRank = allPlayers[index].bestRank(ROUND.community)
            rankProbs[highestRank] = 100

        return rankProbs

#!subprograms
def openNewGame(window, event):
    buttonPressSound.play()
    canvas.destroy()
    titleScreen.runTitleScreen(window)
    exit()

def ingameSettings(event):
    global inGameBgImage, inGameCanvas, exitButton, saveButton, saveNameEntry
    buttonPressSound.play()
    inGameCanvas = tk.Canvas(canvas, width=1516, height=816, borderwidth=0) #creating background for settings
    inGameCanvas.place(x=210, y=140)
    ROUND.timerHide = True #timers showuld be hidden
    allPlayers[ROUND.currPlayer].hideTimer() #hiding the current players timer

    inGameBgImage = ImageTk.PhotoImage(Image.open("../Entities/Background/inGameBack.fw.png")) 
    inGameBg = inGameCanvas.create_image(0, 0, image=inGameBgImage, tags="inGame", anchor=tk.NW) #background image for settings

    exitButton = newButton(inGameCanvas, 30, 30, "settingsExit.fw.png", "inGame", exitSettings) #exit button

    saveButton = newButton(inGameCanvas, 1000, 600, "tealButton.fw.png", "inGame", saveGame) #button to save game
    saveButton.addLabel(inGameCanvas, "SAVE", "white", (1140, 650), 30, "inGame", saveGame)

    saveNameEntry = tk.Entry(inGameCanvas, font=(FONTNAME,20)) #entry box to enter name of saved file
    saveNameEntry.place(x=1000, y=400)

def saveGame(event):
    buttonPressSound.play()
    #validation
    if saveNameEntry.get() == "":
        saveLabel = inGameCanvas.create_text(1000, 500, text="Savename must not be empty"
                    ,font=(FONTNAME,20), fill="white")
    else:
        #TODO saves all attributes to json
        saveLabel = inGameCanvas.create_text(1000, 500, text="Saved to " + str(saveNameEntry.get())
            ,font=(FONTNAME,20), fill="white")


def exitSettings(event):
    inGameCanvas.destroy() #destroying settings canvas and widgets
    ROUND.timerHide = False #timers should be displayed
    allPlayers[ROUND.currPlayer].createTimer() #creating current players timer

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
    global DECK, ROUND, allPositions, allCoOrds, THEUSER

    #*Creating deck of cards
    DECK = Deck()

    for suit in SUITS:
        for value in VALUES:
            DECK.cards.append(Card(suit, value))

    #*getting number of players
    maxPlayers = int(getJson("Settings.json", ("options","MaxPlayer")))
    if maxPlayers == 9: #changing variable to fit with number of players
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
            THEUSER = allPlayers[-1]
        else:
            allPlayers.append(AI(NAMES[i], allPositions[i], i, COLOURS[i], allCoOrds[i][0], allCoOrds[i][1]))
        allPlayers[-1].createBlock()

    for player in allPlayers:
        #automatically dealing blinds and setting current position
        if player.position == "SB":
            player.placeSB()
        elif player.position == "BB":
            player.placeBB()
        elif player.position == "UTG":
            ROUND.currPlayer = player.index
            player.currTurn()
        
    for player in allPlayers:
        DECK.dealPlayer(2, player)

    window.mainloop()

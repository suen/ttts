import re
import random
import time
from threading import Thread

class Player:
	
	def __init__(self, name, symbol, main):
		self.name = name
		self.symbol = symbol
		self.main = main
		self.currentBoard = None
		self.startThread = False
		Thread(target=self.threadPause).start()
	
	def threadPause(self):
		while not self.startThread:
			time.sleep(0.5)
		self.makeMove()
		self.startThread = False
		self.threadPause()
	
	def makeMove(self):
		pass
	
	def get_input(self, text="> "):
		choice = raw_input(text)
		choice = str(choice)

		r = re.match(r'^[a-z][a-z]$', choice)
		if r is None:
			return self.get_input("Enter again > ")
		
		return str(choice)

	def getNextMove(self, currentBoard):
		self.currentBoard = currentBoard		
		return self.get_input()
	
	def makemove(self):
		self.get_input()

class AI(Player):

	def makeMove(self):
		possibleMoves = self.currentBoard.getValidMoves()
		aiChoice = random.randint(0, len(possibleMoves)) - 1
		#if aiChoice >= len(possibleMoves):
			#return self.getNextMove(currentBoard)
		self.main.playerNextMove(self, possibleMoves[aiChoice])
		#return possibleMoves[aiChoice]
	
	def getNextMove(self, currentBoard):
		self.currentBoard = currentBoard
		self.startThread = True

class NetworkPlayer(Player):
	
	def getNextMove(self, currentBoard):
		pass

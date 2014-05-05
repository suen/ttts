import re
import random
import time

class Player:
	
	def __init__(self, name, symbol):
		self.name = name
		self.symbol = symbol
		
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
	
	def getNextMove(self, currentBoard):

		possibleMoves = currentBoard.getValidMoves()
		aiChoice = random.randint(0, len(possibleMoves))
		if aiChoice >= len(possibleMoves):
			return self.getNextMove(currentBoard)
		return possibleMoves[aiChoice]
		

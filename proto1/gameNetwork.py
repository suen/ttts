from player import Player,AI
from board import Board
import time
import signal
import sys

class Game:
	
	def __init__(self):
		self.board = Board(6)
		self.next_player = None
	
	def setPlayer1(self, player1):
		self.player1 = player1
	
	def setPlayer2(self, player2):
		self.player2 = player2

	def setFirstMover(self, player):
		self.next_player = player

	def getNextPlayer(self):
		if self.next_player == self.player1:
			self.next_player = self.player2
		else:
			self.next_player = self.player1
		return self.next_player
	
	def getBoard(self):
		return str(self.board.board)
	
	def gameover(self):
		ifwinner = self.board.check()
		return (ifwinner != "NOT_FULL")
	
	def getWinner(self):
		ifwinner = self.board.check()
		if ifwinner != "NOT_FULL" and len(ifwinner) == 1:
			print(ifwinner + " wins")
			return ifwinner
		else:
			print(ifwinner);
			return "";
	
	def makeMove(self, player, move):
		
		if self.gameover():
			print "Game Over"
			return;
	
		if player != self.next_player:
			print "Illegal move, NOT_YOUR_TURN";
			return;
		
		if not self.board.validateMove(move):
			print "Illegal move, make your move again"
			return;
		
		self.board.write(self.next_player.symbol, move)
		self.next_player = self.getNextPlayer()



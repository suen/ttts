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

	def run(self):

		next_player = self.firstPlayer
		while 1:
			self.board.show_board()
			ifwinner = self.board.check()

			if ifwinner != "NOT_FULL":
				if ifwinner == "FULL":
					print("Nobody wins, game is draw")
				else:
					print(ifwinner + " wins")
				break				

			print(next_player.symbol + " turn")
			time.sleep(1)
					
			coord = next_player.getNextMove(self.board.makeCopy())
			
			if self.board.validateMove(coord):
				self.board.write(next_player.symbol, coord)
			else:
				print("Invalid move: " + str(coord))
				continue
			
			if next_player == self.player1:
				next_player = self.player2
			else:
				next_player = self.player1
			
			
def signal_handler(signal, frame):
	print('\nGraceful exit')
	sys.exit(0)		

def main():
	game = Game()

	player1 = AI("daubajee", "X")
	player2 = AI("Chaku", "O")
	
	game.setPlayer1(player1)
	game.setPlayer2(player2)
	game.setFirstMover(player1)
	
	game.run()

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
#	main()


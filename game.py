from player import Player,AI
from board import Board
import time
import signal
import sys

class Game:
	
	def __init__(self):
		self.board = Board(6)
	
	def setPlayer1(self, player1):
		self.player1 = player1
	
	def setPlayer2(self, player2):
		self.player2 = player2

	def setFirstPlayer(self, player):
		self.firstPlayer = player

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
	game.setFirstPlayer(player1)
	
	game.run()

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	main()


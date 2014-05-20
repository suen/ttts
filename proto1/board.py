import copy
import sys
import traceback


class Board:

	def __init__(self, dimension):
		self.dimension = dimension 
		self.board = self.empty_board(dimension)
		
	def empty_board(self, number):
	    board = []
	    self.board_address = []
	    fl = 97
	    sl = 97
	    for i in range(0,number):
			row = []
			row_address = []
			for j in range(0,number):
				row_address.append( chr(fl) + chr(sl))
				row.append("")
				sl += 1
				if sl > 122:
					sl = 97
					fl += 1
			self.board_address.append(row_address)
			board.append(row)
		
	    return board

	def makeCopy(self):
		return copy.deepcopy(self)

	def show_board(self):
		board = self.board
		ofirst  = " __ "
		osecond = "|  |"
		othird  = "|__|"

		xfirst  ='    '
		xsecond =' \/ '
		xthird  =' /\ '

		for i in range(0, self.dimension):
			row = board[i]
			row_display = []
			
			border = '---------'*self.dimension + '-'
			border = '========='*self.dimension + '='
			print(border)
			row_string1 = "|"
			row_string2 = "|"
			row_string3 = "|"
			row_string4 = "|"
			row_string5 = "|"
			for j in range(0, self.dimension):
				charcter = []
				
				if row[j] == "O":
					charcter.append(ofirst)
					charcter.append(osecond)
					charcter.append(othird)
				elif row[j] == "X":
					charcter.append(xfirst)
					charcter.append(xsecond)
					charcter.append(xthird)
				else:
					charcter.append("    ")
					charcter.append("    ")
					charcter.append("    ")
				row_string1 += "  " + charcter[0] + "  |"
				row_string2 += "  " + charcter[1] + "  |"
				row_string3 += "  " + charcter[2] + "  |"
				row_string4 += "__" + "____" + "__|"
				row_string5 += "  " + " "+self.board_address[i][j]+" " + "  |"
				
				row_display.append(charcter)
			print(row_string1)
			print(row_string2)
			print(row_string3)
			print(row_string4)
			print(row_string5)


		print(border)

	def check(self):
		board = self.board
		dim = self.dimension
	    
		for t in range(0, dim):
			for y in range(0, dim):
				try:
					if board[t][y] == "":
						continue
					elif y+2 <= dim-1 and board[t][y] == board[t][y+1] and board[t][y] == board[t][y+2] :
						return board[t][y]
					elif t+2 <= dim-1 and board[t][y] == board[t+1][y] and board[t][y] == board[t+2][y] :
						return board[t][y]
					elif t+2 <= dim-1 and y+2 <=dim-1 and board[t][y] == board[t+1][y+1] and board[t][y] == board[t+2][y+2] :
						return board[t][y]
					elif t-2 >= 0 and y+2 <=dim-1 and board[t][y] == board[t-1][y+1] and board[t][y] == board[t-2][y+2] :
						return board[t][y]
				except IndexError:
					#print traceback.format_exc()
					print("This is embarassing, but the rule engine just blew off!!!!, please debug for values: " +str(t) +"," + str(y))
					sys.exit(0)	
	    
		full = "FULL"
		for i in range(0, dim):
		    for j in range(0, dim):
				if board[i][j] == "":
					full = "NOT_FULL"
					break
		
		return full


	def write_onboard(self, symbol, point):
		board = self.board

		if board[int(point[0])][int(point[1])] == "":
			board[int(point[0])][int(point[1])] = symbol
		self.board =  board

	def write(self, symbol, coord):
		found = False
		point = []
		for i in range(0, self.dimension):
			for j in range(0, self.dimension):
				if coord in self.board_address[i]:
					found = True
					point = [i, self.board_address[i].index(coord)]
		
		if not found:
			return
		else:
			self.write_onboard(symbol, point)
	
	def validateMove(self, move):
		return True
		
	def getValidMoves(self):
		validMoves = []
		for i in range(0, self.dimension):
			for j in range(0, self.dimension):
				if self.board[i][j] == "":
					validMoves.append(self.board_address[i][j])
					
		return validMoves
		
	def getCoordinates(self):
		return self.board_address


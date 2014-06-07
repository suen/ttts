'''
Created on May 17, 2014

@author: surendra
'''
import copy
import sys


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
        return copy.deepcopy(self.board)

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
        
        if type(point[0]) is str : 
            if board[int(point[0])][int(point[1])] == "":
                board[int(point[0])][int(point[1])] = symbol
        else:
            board[point[0]][point[1]] = symbol
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
        if len(move) != 2:
            return False
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



class TicTacToe:
    
    def __init__(self, player1, player2):
        self.board = Board(6)
        self.next_player = None
        self.player1 = player1;
        self.player2 = player2;
    
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
        return self.board.board;
    
    def setBoard(self, board):
        self.board.board = board;
    
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
        
        self.board.write_onboard(self.next_player[1], move)
        self.next_player = self.getNextPlayer()
     
    def writeSymbol(self, symbol, point):
        self.board.write_onboard(symbol, point)
     
    def boarddiff(self, newboard):
        board = self.getBoard();
        
        found = [];         
        for r in range(0, len(board)):
             for i in range(0, len(board)):
                 if board[r][i] != newboard[r][i]:
                     if len(found) == 0:
                         found = [r,i]
                     else:
                        print "the board has more than one modification"
        return (found, newboard[found[0]][found[1]]);
         
        
class GameRoom:
    
    def __init__(self, name):
        self.name = name;
        #self.creator = creator;
        self.spectators = [];
 
    def addSpectator(self, peer):
        if peer not in self.spectators:
            self.spectators.append(peer);
    
    def getSpectators(self):
        return self.spectators;
 
    def setPlayer1(self, player1):
        self.player1 = player1

    def setPlayer2(self, player2):
        self.player2 = player2
        
    def getPlayer1(self):
        return self.player1
 
    def getPlayer2(self):
        return self.player2
    
    def setFirstPlayer(self, player):
        self.firstplayer = player
    
    def getName(self):
        return self.name;
    
    def getCreator(self):
        return self.name
    
    def gameInit(self):
        self.game = TicTacToe(self.player1, self.player2);
        self.game.setFirstMover(self.firstplayer);

        
    def getGame(self):
        return self.game;

      
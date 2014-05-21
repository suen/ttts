'''
Created on May 17, 2014

@author: surendra
'''

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

        self.makeMoveRequest = False
        self.winCode = 0
        self.gameFinished = False
        
        Thread(target=self.threadPause).start()
        
    def threadPause(self):
        while not self.startThread:
            time.sleep(0.5)
        self.runPlayer()
        self.startThread = False
        self.threadPause()        

    def runPlayer(self):
        pass
    
    def makeMove(self, currentBoard):
        self.currentBoard = currentBoard
        self.makeMoveRequest = True
        self.startThread = True
    
    def gameover(self, currentBoard, winCode):
        self.gameFinished = True
        self.winCode = winCode
        self.startThread = True

class AI(Player):
    
    def getPossibleMoves(self, board):
        validMoves = []
        for i in range(0, 6):
            for j in range(0, 6):
                if board[i][j] == "":
                    validMoves.append([i, j])
                    
        return validMoves
    
    def runPlayer(self):
        if not self.makeMoveRequest or self.currentBoard is None:
            return
        
        possibleMoves = self.getPossibleMoves(self.currentBoard)
        aiChoice = random.randint(0, len(possibleMoves)) - 1
        self.main.playerNextMove(self, possibleMoves[aiChoice])
        

class AsyncPlayer(Player):

    def onWebSocketMessage(self, payload, isBinary):
        self.messageQueue.append(payload)
        self.startThread = True
        pass
    
    def setWebSocket(self, wsocket):
        self.wsocket = wsocket
        self.messageQueue = [];
        self.wsocket.onMessage = self.onWebSocketMessage

    def treatMessage(self):
        if len(self.messageQueue) == 0:
            return False
        
        message = self.messageQueue.pop()
        
        if "TTTS WAITING" in message:
            print "Seems like somebody is waiting"
            print "Let's start a new game then"
            self.main.new_game_init()
            self.wsocket.sendMessage("TTTS START_GAME X")
            pass
                
        elif "TTTS PLAYER_MOVE" in message:
            comma_index = message.find(",")
            xcord = int(message[comma_index-1])
            ycord = int(message[comma_index+1])
            self.main.playerNextMove(self, [xcord, ycord])
            
        elif "PEER_LIST" in message:
            peers = self.main.net.getPeers()
            peerString = "{"
            for i in range(0, len(peers)):
                peer = peers[i]
                peerString += "'" + str(i) + "': '" + str(peer[0]) + "'"
                
                if i != len(peers) - 1 :
                    peerString += ","
            peerString += "}"
            self.wsocket.sendMessage("PEER_LIST " + peerString)

                    
        return True
        
            
    def runPlayer(self):
        if self.wsocket is None:
            print("WebSocket not set for AsyncPlayer, Thread sleeping")
            return
        
        self.treatMessage()
        
        if self.makeMoveRequest:
            boardString = str(self.currentBoard)
            self.wsocket.sendMessage("TTTS BOARD_STATE " + boardString, False)
            self.wsocket.sendMessage("TTTS MAKE_MOVE", False)
            self.makeMoveRequest = False
        
        if self.gameFinished:
            boardString = str(self.currentBoard)
            
            if (self.winCode == 1):
                win = "YOU_WIN"
            elif self.winCode == 2:
                win = "YOU_LOSE"
            else:
                win = "DRAW"
            
            self.wsocket.sendMessage("TTTS BOARDSTATE " + boardString, False)
            self.wsocket.sendMessage("TTTS GAME_OVER " + win, False)        
        
        
class RemotePlayer(Player):
    
    def runPlayer(self):
        pass
        
        
        
        
        
        
        
        
        
        
        
        
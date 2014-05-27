'''
Created on May 17, 2014

@author: surendra
'''

from Network import Network,BroadcastListener
from Game import TicTacToe
from Player import AI, AsyncPlayer
from User import AsyncUser
import time, sys
from threading import Thread

class Main:
    def __init__(self):
        self.breceiver = BroadcastListener(self)
        self.net = Network.Instance()
        self.net.setMain(self)
        self.webClient = None;
        self.startGame = False
        self.board_sent_to_player = False
        self.user = AsyncUser(self)
        self.username = "Daubajee"
        self.broadcastReceived = []
        self.lastBroadcastedMsg = ""

        #self.new_game_init()

    def new_game_init(self):
        print "New Game initializing"
        self.game = TicTacToe()
        #self.player1 = AI("artificial agent", "X", self)
        self.player2 = AI("AI agent", "O", self)
        self.game.setPlayer1(self.player1)
        self.game.setPlayer2(self.player2)
        self.game.setFirstMover(self.player1)
        self.startGame = True
        self.playerHasMoved = False
        self.playerMove = None
        print "New Game started"
            
    def startNetwork(self):
        self.net.startNetwork()

    def connectPeer(self, address, port):
        self.net.connectPeer(address, port);

    def setWebClient(self, client):
        self.user.setWebClient(client);
#        self.player1 = AsyncPlayer("Web Player", "X", self)
#        self.player1.setWebSocket(self.webClient)

    def getPeerList(self):
        return self.net.getPeers()
    
    def onPeerListChange(self):
        print "calling self.user for peer change"
        self.user.onPeerListChange()
    
    def onPeerMsgReceived(self, peerIdentity, msg):
        self.user.onPeerMsgReceived(peerIdentity, msg)
    
    def onBroadcastReceived(self, msgTuple):
        if msgTuple not in self.broadcastReceived:
            self.broadcastReceived.append(msgTuple)
            self.user.onNewBroadcastReceived(msgTuple)              
            
    def setOpponentPlayer(self, opponent):
        self.player2 = opponent
        
    def playerNextMove(self, player, move):
        self.playerMove = move
        self.playerHasMoved = True
        return;
    
    def createNewRoom(self, roomName):
        self.lastBroadcastedMsg = "NEW_ROOM " + roomName
        self.net.sendBroadcast(self.lastBroadcastedMsg);

    def reBroadcastLastMsg(self):
        if self.lastBroadcastedMsg != "":
            self.net.sendBroadcast(self.lastBroadcastedMsg);

 
    def run(self):

        while (self.net is None or 
                self.webClient is None or 
                not self.startGame ):
            print "no work thread sleeping"
            time.sleep(1)
        
        #self.net.sendDataWebPeers("GAME BOARDSTATE " + str(self.game.board.board))    
        
        if self.game.gameover():
            winner = self.game.getWinner();
            if winner == "":
                #self.net.sendDataWebPeers("GAME GAME_OVER NO_WINNER")
                win_code1 = 0;
                win_code2 = 0;
            else:
                win_code1 = 1 if winner == self.player1.symbol else 2
                win_code2 = 1 if winner == self.player2.symbol else 2

            self.player1.gameover(self.game.board.board, win_code1)
            self.player2.gameover(self.game.board.board, win_code2)

            self.startGame = False
        
        if not self.playerHasMoved:
            if not self.board_sent_to_player: 
                self.game.next_player.makeMove(self.game.board.makeCopy())
                print "Asking for player input"
                self.board_sent_to_player = True
        else:
            coord = self.playerMove
            self.game.makeMove(self.game.next_player, coord)
            self.playerHasMoved = False
            self.playerMove = None
            self.board_sent_to_player = False
        
        time.sleep(1)
        self.run()
        

def main():
    m = Main()
    Thread(target=m.run).start()
    m.startNetwork()


if __name__ == '__main__':
    main()


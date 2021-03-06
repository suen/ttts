'''
Created on May 17, 2014

@author: surendra
'''

from Network import Network,BroadcastListener
from twisted.internet import reactor
from Game import TicTacToe, GameRoom
from Player import AI, AsyncPlayer
from User import AsyncUser
import time, sys, signal, os
import Crypto.PublicKey.RSA as RSA
from threading import Thread
import ConfigParser

class Main:
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read("config.ini")
           
        self.username = config.get('user', 'username');
        self.broadcastAddress = config.get('network', 'broadcastAddress')
        self.UDPPort = int(config.get('network', 'UDPPort'))
        self.TCPPort = int(config.get('network', 'TCPPort'))
        self.WebSocketPort = int(config.get('network', 'WebSocketPort'))

        try:
            self.privateKeyPath = config.get('user', 'privateKey')
            if os.path.isfile(self.privateKeyPath):
                self.rsaKey = RSA.importKey((open(self.privateKeyPath, "r")).read())
                if self.rsaKey is not None :
                    print "RSA Key loaded successfully"
            else:
                self.rsaKey = None
                print "no private found, generate one for distributed score system"
        except ConfigParser.NoOptionError:
            pass
        self.config = config
        
        self.breceiver = BroadcastListener(self)
        
        self.net = Network.Instance()
        self.net.setBroadcastAddress(self.broadcastAddress)
        self.net.setUDPPort(self.UDPPort)
        self.net.setTCPPort(self.TCPPort)
        self.net.setWebSocketPort(self.WebSocketPort)
        self.net.setMain(self)

        self.webClient = None;
        self.startGame = False
        self.board_sent_to_player = False
        self.user = AsyncUser(self)

        self.broadcastReceived = []
        self.lastBroadcastedMsg = ""
            
        signal.signal(signal.SIGINT, self.signal_handler)

        self.die = False
        #self.gameLoopThread = Thread(target=self.run)
        #self.gameLoopThread.start()
        
        Thread(target=self.startWebclient).start()
        
        self.startNetwork()

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
        self.die = True
    
    def startWebclient(self):
        os.system("/usr/bin/google-chrome ../web/index.html")
        return
    
    def connectPeer(self, address, port):
        self.net.connectPeer(address, port);

    def setWebClient(self, client):
        print "new webclient"
        self.user = AsyncUser(self)
        self.user.setWebClient(client);
#        self.player1 = AsyncPlayer("Web Player", "X", self)
#        self.player1.setWebSocket(self.webClient)

    def getPeerList(self):
        return self.net.getPeers()
  
    def getPeerById(self, peerId):
        return self.net.getPeerById(peerId)
    
    def getPeerByIP(self, peerIp):
        return self.net.getPeerByIP(peerIp)
    
    def onPeerListChange(self):
        print "calling self.user for peer change"
        self.user.onPeerListChange()
    
    def sendMessage(self, peerId, message):
        for (id, p, ip) in self.getPeerList():
            if id == peerId:
                p.sendLine(message)
    
    
    def onPeerMsgReceived(self, peerIdentity, msg):
        self.user.onPeerMsgReceived(peerIdentity, msg)
    
    def onBroadcastReceived(self, msgTuple):
        datagram,peerIdentity = msgTuple;
        
        broadcastingPeer = self.net.getPeerByIP(peerIdentity[0])
        
        if broadcastingPeer is None:
            self.connectPeer(peerIdentity[0], peerIdentity[1]);
            return
        
        if msgTuple not in self.broadcastReceived:
            #self.broadcastReceived.append(msgTuple)
            self.user.onNewBroadcastReceived((broadcastingPeer.peerName, datagram))              
            
    def setOpponentPlayer(self, opponent):
        self.player2 = opponent
        
    def playerNextMove(self, player, move):
        self.playerMove = move
        self.playerHasMoved = True
        return;
    
    def createNewRoom(self, roomName):
        self.gameRoom = GameRoom(roomName)
        print "Creating a new room " + self.gameRoom.getName()


    def reannounceRoom(self):
        print "Multicasting created room " + self.gameRoom.getName()
        self.net.sendMulticast("NEW_ROOM " + self.gameRoom.getName())
    
    def getGameRoom(self):
        return self.gameRoom

    def sendMulticast(self, msg):
        self.net.sendMulticast(msg)
        
    def broadcast(self):
        self.net.broadcast();

    def getUsername(self):
        return self.username
 
    def generateKey(self):
        self.rsaKey = RSA.generate(2048, os.urandom);
    
        fw = open("private.key", "w")
        fw.write(self.rsaKey.exportKey());
        fw.close()
    
        self.config.set("user", "privateKey", "private.key")
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)
        print "RSA Key generated and written to key and included to config.ini"

    def getPublicKey(self):
        return self.rsaKey.publickey()

    def getPublicKeyString(self):
        return self.rsaKey.publickey().exportKey()
 
    def run(self):

        while (self.net is None or 
                self.webClient is None or 
                not self.startGame ):
            print "No game, GameLoopThread sleeping"
            if self.die:
                return
            time.sleep(10)
        
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

    def signal_handler(self, signal, frame):
        print 'KeyBoard Interrupt',signal
        print 'Graceful Exit'
        self.die = True
        reactor.callFromThread(reactor.stop)





if __name__ == '__main__':
    m = Main()
    
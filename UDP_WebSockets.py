
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import time
from socket import SOL_SOCKET, SO_BROADCAST
from threading import Thread
import sys
from singleton import Singleton
from gameNetwork import Game
from player import AI

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory

class UDPBroadcaster(DatagramProtocol):
	
	def __init__(self, address, breceiver):
		self.broadcastAddress = address
		self.breceiver = breceiver
		self.broadcastMsg = ""
		self.startBroadcast = False
	
	def setMsgToBroadcast(self, message):
		self.broadcastMsg = message
		self.startBroadcast = True
		print "UDP broadcast started"
		
	def stopBroadcast(self):
		self.startBroadcast = False
		self.broadcastMsg = ""
		print "UDP broadcast stopped" 
		
	def startProtocol(self):
		self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
		Thread(target=self.doInfiniteBroadcast).start()
		print "UDP protocol initiated, ready for broadcast" 
	
	def doInfiniteBroadcast(self):
		while 1:
			if self.startBroadcast:
				self.transport.write(self.broadcastMsg, self.broadcastAddress)
			time.sleep(2)
 

	def datagramReceived(self, datagram, address):
		if datagram == self.broadcastMsg:
			return
		print 'Datagram received: ', repr(datagram)
		self.breceiver.onBroadcastReceived((datagram, address))

	def getBroadcastListener():
		pass
		
	
class MyServerProtocol(WebSocketServerProtocol):

	def onConnect(self, request):
		print("Client connecting: {0}".format(request.peer))
		Network.Instance().addPeer(self)

	def onOpen(self):
		print("WebSocket connection open.")

	def onMessage(self, payload, isBinary):
		if isBinary:
			print("Binary message received: {0} bytes".format(len(payload)))
			self.sendMessage(payload, isBinary)
			return
		msg = payload.decode('utf8')
		Network.Instance().treat(self, msg)
		#self.sendMessage(msg, isBinary)
		print("Text message received: {0}".format(payload.decode('utf8')))

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {0}".format(reason))
		Network.Instance().removePeer(self)

	
@Singleton
class Network:
	
	def __init__(self):
		self.broadcastReceiver = None
		self.broadcaster = None
		self.websocketFactory = None
		self.webconnections = []
	
	def setMain(self, main):
		self.main = main

	def addPeer(self, peer):
		if peer not in self.webconnections:
			self.webconnections.append(peer)
			print "passing peer"
			self.main.setWebClient(peer)
	
	def removePeer(self, peer):
		if peer in self.webconnections:
			self.webconnections.remove(peer)

	def startNetwork(self):
		self.broadcaster = UDPBroadcaster(("192.168.1.255", 8000), self)
		reactor.listenUDP(8000, self.broadcaster)

		self.websocketFactory = WebSocketServerFactory("ws://localhost:9000", debug = False)
		self.websocketFactory.protocol = MyServerProtocol 
		reactor.listenTCP(9000,self.websocketFactory)
		reactor.run()

	def sendDataWebPeers(self, data):
		for wpeers in self.webconnections:
			wpeers.sendMessage(data, False)

	def treat(self, peer, msg):
		print msg
		self.main.onWebPeerMessage(peer, msg)
		#return str(len(self.webconnections)) + " peers connected"
		
	#UDP broadcast
	def sendBroadcast(self, msg):
		self.broadcaster.setMsgToBroadcast(msg)	
		pass
	
	def stopBroadcast(self):
		self.broadcaster.stopBroadcast()
	
	def broadcastReceived(self, dtuple):
		print dtuple, " RECEIVED"
			
	#TCP receiver
	def setReceiver(self, receiver):
		pass
	
	#TCP sender
	def sendmsg(self, msg, address):
		pass




class BroadcastListener():

	def __init__(self, main):
		self.main = main

	def onBroadcastReceived(self, dtuple):
		self.main.broadcastReceived(dtuple)
	

class Main:
	def __init__(self):
		self.breceiver = BroadcastListener(self)
		self.net = Network.Instance()
		self.net.setMain(self)
		self.webClient = None;
		self.startGame = False
		#self.new_game_init()

	def new_game_init(self):
		print "New Game initializing"
		self.game = Game()
		self.player1 = AI("artificial agent", "X", self)
		self.player2 = AI("artificial agent 2", "O", self)
		self.game.setPlayer1(self.player1)
		self.game.setPlayer2(self.player2)
		self.game.setFirstMover(self.player1)
		self.startGame = True
		self.playerHasMoved = False
		self.playerMove = None
		print "New Game started"
			
	def startNetwork(self):
		self.net.startNetwork()

	def getNextAction(self):
		if len(self.msgsToSend) == 0:
			return "";
		head = self.msgsToSend[len(self.msgsToSend) - 1];
		self.msgsToSend.remove(head);
		return head;

	def setWebClient(self, client):
		self.webClient = client
		#self.new_game_init()

	def onWebPeerMessage(self, webConnection, msg):
		print "MESSAGE FROM CLIENT " + msg
		self.new_game_init()
		pass
		
	def playerNextMove(self, player, move):
		self.playerMove = move
		self.playerHasMoved = True
		return;
		
	def run(self):

		board_sent_to_player = False
		while (self.net is None or 
				self.webClient is None or 
				not self.startGame ):
			print "no work thread sleeping"
			time.sleep(1)
		
		self.net.sendDataWebPeers("HEARTBEAT")
		
		self.net.sendDataWebPeers("GAME BOARDSTATE " + str(self.game.board.board))	
		
		if self.game.gameover():
			winner = self.game.getWinner();
			if winner == "":
				self.net.sendDataWebPeers("GAME GAME_OVER NO_WINNER")
			else:
				self.net.sendDataWebPeers("GAME GAME_OVER WINNER " + winner);
			self.startGame = False
		
		if not self.playerHasMoved:
			if not board_sent_to_player: 
				self.game.next_player.getNextMove(self.game.board.makeCopy())
				board_sent_to_player = True
		else:
			coord = self.playerMove
			self.game.makeMove(self.game.next_player, coord)
			self.playerHasMoved = False
			self.playerMove = None
			board_sent_to_player = False
		
		time.sleep(1)
		self.run()
		

def main():
	m = Main()
	Thread(target=m.run).start()
	m.startNetwork()

			
def signal_handler(signal, frame):
	print('\nGraceful exit')
	sys.exit(0)	


if __name__ == '__main__':
   main()
   signal.signal(signal.SIGINT, signal_handler)

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import time
from socket import SOL_SOCKET, SO_BROADCAST
from threading import Thread
import sys
from singleton import Singleton

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory


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
		msg = Network.Instance().treat(self, msg)
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

	def addPeer(self, peer):
		if peer not in self.webconnections:
			self.webconnections.append(peer)
	
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

	def treat(self, peer, msg):
		print msg
		return str(len(self.webconnections)) + " peers connected"
		
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
		

class BroadcastListener():

	def __init__(self, main):
		self.main = main

	def onBroadcastReceived(self, dtuple):
		self.main.broadcastReceived(dtuple)
	

class Main:
	def __init__(self):
		self.breceiver = BroadcastListener(self)
		self.net = Network.Instance()
		pass
	
	def startNetwork(self):
		self.net.startNetwork()

	def run(self):
		
		while(self.net is None):
			time.sleep(2)
		
		if len(Network.Instance().webconnections) > 0:
			peer = Network.Instance().webconnections[0]
			peer.sendMessage("Server heartbeat", False)

		time.sleep(2)
		self.run()

def main():
	m = Main()
	Thread(target=m.run).start()
	m.startNetwork()


if __name__ == '__main__':
   main()

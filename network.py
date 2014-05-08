from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import time
from socket import SOL_SOCKET, SO_BROADCAST
from threading import Thread
import sys

class Network:
	
	def __init__(self, breceiver):
		self.broadcaster = UDPBroadcaster(("192.168.1.255", 8000), breceiver)
		reactor.listenUDP(0, self.broadcaster)
		
	def run(self):
		reactor.run()

	#UDP broadcast
	def sendBroadcast(self, msg):
		self.broadcaster.setMsgToBroadcast(msg)	
		pass
	
	def stopBroadcast(self):
		self.broadcaster.stopBroadcast()

	
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


class BroadcastListener():

	def __init__(self, main):
		self.main = main

	def onBroadcastReceived(self, dtuple):
		self.main.broadcastReceived(dtuple)
	

class Main:
	def __init__(self):
		self.breceiver = BroadcastListener(self)
		self.net = None
		pass
	
	def startNetwork(self):
		self.net = Network(self.breceiver)
		self.net.run()

	def broadcastReceived(self, dtuple):
		print dtuple, " RECEIVED"

	def userconsole(self):
		
		while(self.net is None):
			time.sleep(2)

		cmd = raw_input("> ")

		if cmd == "":
			sys.exit(0)
			return
		elif cmd == "start":
			self.net.sendBroadcast("broadcast message")
		elif cmd == "stop":
			self.net.stopBroadcast()

		self.userconsole()

	def run(self):
		self.userconsole()
	


def main():
	m = Main()	
	Thread(target=m.run).start()
	m.startNetwork()


if __name__ == '__main__':
   main()

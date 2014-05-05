from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import time
from socket import SOL_SOCKET, SO_BROADCAST
from threading import Thread

class Network:
	
	def __init__(self):
		self.broadcaster = UDPBroadcaster(("192.168.1.255", 8000))
		self.broadcaster.setMsgToBroadcast("hello world")
		t = reactor.listenUDP(0, self.broadcaster)
		reactor.run()
		print "broadcaster running"
		
	#UDP broadcast
	def sendBroadcast(self):
		pass
	
	#UDP broadcast receiver
	def setBroadcastReceiver(self, breceiver):
		pass
	
	#TCP receiver
	def setReceiver(self, receiver):
		pass
	
	#TCP sender
	def sendmsg(self, msg, address):
		pass


class UDPBroadcaster(DatagramProtocol):
	
	def __init__(self, address):
		self.broadcastAddress = address
		self.broadcastMsg = ""
		self.startBroadcast = False
	
	def setMsgToBroadcast(self, message):
		self.broadcastMsg = message
		self.startBroadcast = True
		
	def stopBroadcast(self):
		self.startBroadcast = False
		self.broadcastMsg = ""
		
	def startProtocol(self):
		self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
		Thread(target=self.doInfiniteBroadcast).start()
	
	def doInfiniteBroadcast(self):
		while 1:
			if self.startBroadcast:
				self.transport.write(self.broadcastMsg, self.broadcastAddress)
			time.sleep(2)
 

	def datagramReceived(self, datagram, address):
		if datagram == self.broadcastMsg:
			return
		print 'Datagram received: ', repr(datagram)



def main():
	Network()
	


if __name__ == '__main__':
   main()

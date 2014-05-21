
import time;

class User:
	def __init__(self):
		pass
	

class AsyncUser(User):
	
	def __init__(self, main):
		self.webclient = None
		self.main = main
		self.duplicates = [];
	
	def setWebClient(self, webclient):
		if self.webclient is not None and self.webclient != webclient:
			time.sleep(0.5)
			self.duplicates.append(webclient)
			webclient.onMessage = self.onDuplicateClientMessage
			return
		
		if self.webclient == webclient:
			self.webclient = None
			return
		
		self.webclient = webclient
		self.webclient.onMessage = self.onWebClientMessage
	
	def onDuplicateClientMessage(self,msg,isBinary):
		print "SENDING DUPLICATES MESSAGES TO WEBCLIENTS"
		for dupli in self.duplicates:
			dupli.sendMessage("DUPLICATE_WEBCLIENT")
		self.duplicates = []
		
	
	def onPeerListChange(self):
		print "Sending Peer List to webclient"
		peers = self.main.getPeerList()
		peerString = "{"
		for i in range(0, len(peers)):
			peer = peers[i]
			peerString += "\"" + str(i) + "\": \"" + str(peer[0]) + "\""
			
			if i != len(peers) - 1 :
				peerString += ","
		peerString += "}"
		self.webclient.sendMessage("PEER_LIST " + peerString)

	def sendChatMessage(self, peer, message):
		pass
	
	def onChatMessage(self, peer, message):
		pass
	
	def onWebClientMessage(self, msg, isBinary):	
		print "AsyncUser action [" +  msg + "]"
		
		if "PEER_LIST" in msg:
			self.onPeerListChange()
			
		if "CHAT" in msg:
			peers = self.main.getPeerList()
			for peer in peers:
				peer[1].sendLine(msg)
		
		#self.webclient.sendMessage("I will serving you very soon, have patience")
		
		
		
		
		
		

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
	
	
	def onNewBroadcastReceived(self, msgTuple):
		self.webclient.sendMessage("NEW_BROADCAST " + str(msgTuple) )	
	
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
		self.webclient.sendMessage("CHAT " + peer + " " + message)
		pass
	
	def onPeerMsgReceived(self, peerIdentity, msg):
		
		if "CHAT" in msg:
			self.onChatMessage(peerIdentity, msg[5:])
		print "AsyncUser treating TCP msg: " + msg

	
	def onWebClientMessage(self, msg, isBinary):	
		print "AsyncUser action [" +  msg + "]"
		
		if "PEER_LIST" in msg:
			self.onPeerListChange()
			
		if "CHAT" in msg:
			msg = msg[5:]
			id_peer = int(msg[0: msg.find("_")])			
			
			msg = msg[msg.find(" ")+1:]
			
			peers = self.main.getPeerList()
			peers[id_peer][1].sendLine("CHAT " + msg);
			
		if "CREATE_ROOM" in msg:
			roomName = msg[12:]
			self.main.createNewRoom(roomName);
			self.webclient.sendMessage("NEW_ROOM BROADCAST DONE")
		
		if "REBROADCAST" in msg:
			self.main.reBroadcastLastMsg()
			
		#	for peer in peers:
		#		peer[1].sendLine(msg)
		
		#self.webclient.sendMessage("I will serving you very soon, have patience")
		
		
		
		
		
		

import time;

class User:
	def __init__(self):
		pass
	

class AsyncUser(User):
	def __init__(self, main):
		self.webclient = None
		self.main = main
		self.duplicates = [];
		self.clientstate = "NONE";
	
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
		broadcastingPeer,datagram = msgTuple;
		
		print "Sending Datagram to webclient " + datagram;
		if "NEW_ROOM" in datagram:
			self.webclient.sendMessage(datagram + " " + broadcastingPeer )
		else:
			print "BROADCAST RECEIVED, msgType not implemented: " + datagram
	
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
		
		print "PRINTING PEER MSG::" + msg + " FROM: " + peerIdentity
		
		if "CHAT" in msg:
			self.onChatMessage(peerIdentity, msg[5:])

		if "NEW_ROOM" in msg:
			self.webclient.sendMessage(msg + " " + peerIdentity)
		
		if "JOIN_ROOM" in msg:
			room = msg[10:]
			self.webclient.sendMessage("JOIN_ROOM " + peerIdentity + " " + room)
		
		if "ACCEPTED_FOR" in msg:
			room = msg[13:]
			self.webclient.sendMessage("ACCEPTED_FOR " + peerIdentity + " " + room)	
		
		if "CAN_WATCH" in msg:
			room = msg[10:]
			self.webclient.sendMessage("CAN_WATCH " + peerIdentity + " " + room)	
		
		if "START_GAME" in msg:
			room = msg[11:]
			self.webclient.sendMessage("START_GAME " + peerIdentity + " " + room)	
		
		if "START_OK" in msg:
			room = msg[9:];
			self.webclient.sendMessage("START_OK " + peerIdentity + " " + room)	
	
		print "AsyncUser treating TCP msg: " + msg

	
	def onWebClientMessage(self, msg, isBinary):	
		print "AsyncUser action [" +  msg + "]"
		
		if "PEER_LIST" in msg:
			self.onPeerListChange()
			
		if "CHAT" in msg:
			print msg
			msg = msg[5:]
			id_peer = int(msg[0: msg.find("_")])			
			
			msg = msg[msg.find(" ")+1:]
			
			peers = self.main.getPeerList()
			
			peers[id_peer][1].sendLine("CHAT " + msg);
			
		if "CREATE_ROOM" in msg:
			roomName = msg[12:]
			self.main.createNewRoom(roomName);
			self.webclient.sendMessage("NEW_ROOM BROADCAST DONE")

		if "REANNOUNCE_CREATED_ROOM" in msg:
			self.main.reannounceRoom();
		
		if "BROADCAST" in msg:
			self.main.broadcast()
		
		if "JOIN_ROOM" in msg:
			print msg
			msg = msg[10:]
			
			roomName = msg[0:msg.find(" ")]
			msg = msg[msg.find(" ")+1:].strip()
			id_peer = int(msg[0: msg.find("_")])			
			peers = self.main.getPeerList()
			
			peers[id_peer][1].sendLine("JOIN_ROOM " + roomName);
			
		if "ACCEPT_PEER" in msg:
			msg = msg[12:]
			
			roomName = msg[0:msg.find(" ")]
			msg = msg[msg.find(" ")+1:].strip()
			id_peer = int(msg[0: msg.find("_")])			
			peers = self.main.getPeerList()
			
			peers[id_peer][1].sendLine("ACCEPTED_FOR " + roomName);			
			
		if "CAN_WATCH" in msg:
			msg = msg[10:];

			roomName = msg[0:msg.find(" ")]
			msg = msg[msg.find(" ")+1:].strip()
			id_peer = int(msg[0: msg.find("_")])			
			peers = self.main.getPeerList()
			peers[id_peer][1].sendLine("CAN_WATCH " + roomName);			
		
		
		if "START_GAME" in msg:
			msg = msg[11:];

			roomName = msg[0:msg.find(" ")]
			msg = msg[msg.find(" ")+1:].strip()
			id_peer = int(msg[0: msg.find("_")])			
			peers = self.main.getPeerList()
			peers[id_peer][1].sendLine("START_GAME " + roomName);
		
		if "START_OK" in msg:
			msg = msg[9:];
			roomName = msg[0:msg.find(" ")]
			msg = msg[msg.find(" ")+1:].strip()
			id_peer = int(msg[0: msg.find("_")])			
			peers = self.main.getPeerList()
			peers[id_peer][1].sendLine("START_OK " + roomName);					
		
		
		
		
		
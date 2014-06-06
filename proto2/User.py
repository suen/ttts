
import time;

class WebSocketMessageParseException:
	pass

class WebSocketMessage:

	def __init__(self, message):
		pass
	
	@staticmethod
	def parse(message):
		a = "0_daubajee CHAT hi how you are doing"
		s1 = message.find(" ")
		s2 = message.find(" ", s1+1)

		if s1 == -1:
			raise WebSocketMessageParseException
		
		peerIdentity = message[0:s1]
		prefix = message[s1+1: s2] if s2 > s1+1 else message[s1+1:]
		content = message[s2+1:] if s2 > s1 else ""
		return peerIdentity, prefix, content;
	
	@staticmethod
	def create(sender, prefix, content):
		return "%s %s %s"%(sender,prefix,content);
	

class PeerMessage:
	@staticmethod
	def create(prefix, content):
		return prefix + " " + content

	@staticmethod
	def parse(message):
		s1 = message.find(" ")
		return message[0:s1], message[s1+1:]


class User:
	def __init__(self):
		pass
	

class AsyncUser(User):
	def __init__(self, main):
		self.webclient = None
		self.main = main
		self.duplicates = [];
		self.clientstate = "NONE";
		self.game = None;
		self.player = None;
		self.opponent = None;
		self.spectators = [];
	
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
			dupli.sendMessage("local DUPLICATE_WEBCLIENT")
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
		msgstr = WebSocketMessage.create("local", "PEER_LIST", peerString)
		self.webclient.sendMessage(msgstr)
		
	def onPeerMsgReceived(self, peerIdentity, msg):
		
		print "<<<<<<Peer msg"
		print "Peer: [" + peerIdentity + "]"
		
		prefix, msgContent = PeerMessage.parse(msg);
		msgContent = msgContent.strip()
		
		print "PREFIX: [" + prefix + "]"
		print "CONTENT: [" + msgContent + "]"
		
		if "CHAT" == prefix:
			self.webclient.sendMessage(peerIdentity  + " CHAT " + msgContent)

		if "NEW_ROOM" == prefix:
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
		
		if "JOIN_ROOM" == prefix:
			self.main.createNewRoom(msgContent.strip());
			self.gameRoom = self.main.getGameRoom();
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
		
		if "ACCEPT_PEER" == prefix:
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
		
		if "CAN_WATCH" == prefix:
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
		
		if "START_GAME" == prefix:
			msg = "START_GAME %s player2: %s spectators: %s"
			
			p2ip = re.search(r'2\: [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', msgContent).group()[3:].strip()
			s1ip = re.search(r's\: [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', msgContent).group()[3:].strip()
			
			p1peer = self.main.getPeerById(peerIdentity)
			p2peer = self.main.getPeerByIp(p2ip)
			s1peer = self.main.getPeerByIp(s1ip);
			
			
						
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
		
		if "READY_GAME" == prefix:
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
	
		print ">>>>>>"

	
	def onWebClientMessage(self, msg, isBinary):	
		print "<<<<<<Webclient msg"
		print "Msg: [" + msg + "]"
		
		peerIdentity, msgPrefix, msgContent = WebSocketMessage.parse(msg);
		
		if "PEER_LIST" == msgPrefix:
			self.onPeerListChange()
			
		if "CHAT" == msgPrefix:
			self.main.sendMessage(peerIdentity, "CHAT " + msgContent);
			
		if "CREATE_ROOM" == msgPrefix:
			self.main.createNewRoom(msgContent.strip());
			self.gameRoom = self.main.getGameRoom();
			self.main.sendMulticast("NEW_ROOM " + self.gameRoom.getName())
		
		if "REANNOUNCE_CREATED_ROOM" == msgPrefix:
			self.main.reannounceRoom();
		
		if "BROADCAST" == msgPrefix:
			self.main.broadcast()
		
		if "JOIN_ROOM" == msgPrefix:
			roomName = msgContent.strip()
			self.main.createNewRoom(roomName);
			self.gameRoom = self.main.getGameRoom();
			self.main.sendMessage(peerIdentity, "JOIN_ROOM " + roomName);
			
		if "ACCEPT_PEER" == msgPrefix:
			roomName = msgContent.strip()
			self.gameRoom.setPlayer2(peerIdentity);
			self.main.sendMessage(peerIdentity, "ACCEPT_PEER " + roomName);

		if "CAN_WATCH" == msgPrefix:
			roomName = msgContent.strip()
			self.gameRoom.addSpectator(peerIdentity);
			self.main.sendMessage(peerIdentity, "CAN_WATCH " + roomName);
		
		if "START_GAME" == msgPrefix:
			roomName = msgContent.strip()
			
			p2peer = self.main.getPeerById(self.gameRoom.getPlayer2())
			s1peer = self.main.getPeerById(self.gameRoom.getSpectators()[0])
			msg = "START_GAME %s player2: %s spectators: %s"%(roomName, p2peer.ip, s1peer.ip)
			
			self.main.sendMulticast(msg)
		
		if "READY_GAME" == msgPrefix:
			roomName = msgContent.strip()
			self.main.sendMessage(peerIdentity, "READY_GAME " + roomName);		

		print ">>>>>>"		
		
		
		
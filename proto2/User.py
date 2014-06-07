
import time, re, json;

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
		message += " "
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
	
	def getSelfIP(self):
		return self.main.getPeerList()[0][1].transport.getHost().host;
	
	def scoreboard(self, p1peer, p2peer, s1peer, winner):
		p1key = p1peer[2].publickey if p1peer[2] is not None else self.main.getPublicKey()
		p2key = p2peer[2].publickey if p2peer[2] is not None else self.main.getPublicKey()
		s1key = s1peer[2].publickey if s1peer[2] is not None else self.main.getPublicKey()
		
		if p1peer[2] is None:
			#player1
			pass
		
		
		print "<<Score board>>"
		print 
		print p2peer
		print s1peer
		print winner
		print "<<score board>>"
	
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
			self.playingAs = ("player2", "O");
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
		
		if "CAN_WATCH" == prefix:
			self.playingAs = ("spectator", "+");
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
		
		if "START_GAME" == prefix:
			gameparam = json.loads(msgContent);
			
			p1peer = self.main.getPeerById(peerIdentity)
			myip = self.getSelfIP()
			
			p2peer = self.main.getPeerByIP(gameparam['player2']) if gameparam['player2'] != myip else None;
			s1peer = self.main.getPeerByIP(gameparam['spectators']) if gameparam['spectators'] != myip else None;

			p1name = p1peer.peerName
			p2name = p2peer.peerName if p2peer is not None else self.main.getUsername()
			s1name = s1peer.peerName if s1peer is not None else self.main.getUsername()

						
			p1tuple = (p1name, "X", p1peer)
			p2tuple = (p2name, "O", p2peer)

			self.myplayer = p2tuple;

			self.gameRoom.setPlayer1(p1tuple);
			self.gameRoom.setPlayer2(p2tuple);
			self.gameRoom.addSpectator((s1name, "+", s1peer));
			self.gameRoom.setFirstPlayer(p1tuple);
			self.gameRoom.gameInit();
			self.game = self.gameRoom.getGame();

			msg = '{"roomName": "%s","player1": "%s", "player2": "%s", "spectators": "%s", "yourSymbol": "%s", "firstPlay": "player1"}'%(gameparam['roomName'], p1name, p2name, s1name, self.playingAs[1])
			msg = msg.encode('ascii');
			print "<<<<"+ str(type(msg)) + " " + msg + ">>>>>"
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msg))
			print "My symbol is: " + self.playingAs[1]
		
		if "READY_GAME" == prefix:
			self.webclient.sendMessage(WebSocketMessage.create(peerIdentity, prefix, msgContent))
	
		if "TTTS_BOARD" == prefix:
			board = json.loads(msgContent.strip());
			self.game.setBoard(board);
			newboard = json.dumps(self.game.getBoard());

			self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_BOARD", newboard))
			if self.game.gameover():
				winner = self.game.getWinner();
				if winner  == "":
					self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_GAME_OVER", "nobody wins"))
				else: 
					winner = winner + " wins"
					self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_GAME_OVER", winner.encode("ascii")))
				
				self.scoreboard(self.gameRoom.getPlayer1(), self.gameRoom.getPlayer2(), 
							self.gameRoom.getSpectators()[0], winner)

	
		if "TTTS_MAKE_MOVE" == prefix:
			self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_MAKE_MOVE", ""))
	
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
			
			p2tuple = (self.main.getPeerById(peerIdentity).peerName, "O", self.main.getPeerById(peerIdentity))
			self.gameRoom.setPlayer2(p2tuple);
			self.main.sendMessage(peerIdentity, "ACCEPT_PEER " + roomName);

		if "CAN_WATCH" == msgPrefix:
			roomName = msgContent.strip()
			p2tuple = (self.main.getPeerById(peerIdentity).peerName, "+", self.main.getPeerById(peerIdentity))
			self.gameRoom.addSpectator(p2tuple);
			self.main.sendMessage(peerIdentity, "CAN_WATCH " + roomName);
		
		if "START_GAME" == msgPrefix:
			roomName = msgContent.strip()
			self.playingAs = ("player1", "X");

			p2peer = self.gameRoom.getPlayer2()
			s1peer = self.gameRoom.getSpectators()[0]
			selfip = self.getSelfIP()
			
			p1tuple = (self.main.getUsername(), "X", None)
			self.myplayer = p1tuple
			
			self.gameRoom.setPlayer1(p1tuple);
			self.gameRoom.setFirstPlayer(p1tuple);
			self.gameRoom.gameInit();
			self.game = self.gameRoom.getGame();
			
			msg = '''START_GAME {"roomName": "%s", "player1": "%s", "player2": "%s", "spectators": "%s", "player1Symbol": "X", "player2Symbol": "O", "firstPlay": "player1"}'''%(roomName, selfip, p2peer[2].ip, s1peer[2].ip)
			
			msgloopback = '''{"roomName": "%s", 
					"player1": "local", 
					"player2": "%s", 
					"spectators": "%s",
					"yourSymbol": "%s", 
					"firstPlay": "player1"}'''%(roomName, p2peer[2].peerName, s1peer[2].peerName,self.playingAs[1])			
			
			self.webclient.sendMessage(WebSocketMessage.create("local","START_GAME", msgloopback))
			self.main.sendMulticast(msg)
			print "My symbol is: " + self.playingAs[1]
		
		if "READY_GAME" == msgPrefix:
			roomName = msgContent.strip()
			self.main.sendMessage(peerIdentity, "READY_GAME " + roomName);
			
			
		if "TTTS_MOVE" == msgPrefix:
			
			if self.playingAs[1] == "+":
				return
			
			move = json.loads(msgContent.strip());
			game = self.gameRoom.getGame();
			print "writing "+ self.playingAs[1] + " to board"
			game.writeSymbol(self.playingAs[1], move[1]);
			
			newboard = json.dumps(game.getBoard());
			print "result: " + newboard
			
			msg = 'TTTS_BOARD ' + newboard;
			
			self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_BOARD", newboard))
			self.main.sendMulticast(msg)

			if self.game.gameover():
				winner = self.game.getWinner();
				if winner  == "":
					self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_GAME_OVER", "nobody wins"))
				else: 
					winner = winner + " wins"
					self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_GAME_OVER",winner.encode("ascii") ))
				
				self.scoreboard(self.gameRoom.getPlayer1(), self.gameRoom.getPlayer2(), 
							self.gameRoom.getSpectators()[0], winner)

			else:
				self.main.sendMulticast("TTTS_MAKE_MOVE")
		
		if "NEW_RSA" == msgPrefix:
			self.main.generateKey() 


		print ">>>>>>"		
		
		
		
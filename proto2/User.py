
import time, re, json, hashlib;
from ring import Ring
import Crypto.PublicKey.RSA as RSA
import sqlite3

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
		self.rings = []
		self.ringCount = []
		self.summary = None;
		self.validrings = []
		self.dbwritten = False;
	
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
	
	def createScoreFile(self, p1peer, p2peer, s1peer, winner):
		p1key = p1peer[2].publickey.publickey().exportKey() if p1peer[2] is not None else self.main.getPublicKeyString()
		p2key = p2peer[2].publickey.publickey().exportKey() if p2peer[2] is not None else self.main.getPublicKeyString()
		s1key = s1peer[2].publickey.publickey().exportKey() if s1peer[2] is not None else self.main.getPublicKeyString()
		
		p1name = p1peer[0][p1peer[0].find("_")+1:] if p1peer[0].find("_") > 0 else p1peer[0]
		p2name = p2peer[0][p2peer[0].find("_")+1:] if p2peer[0].find("_") > 0 else p2peer[0]
		s1name = s1peer[0][s1peer[0].find("_")+1:] if s1peer[0].find("_") > 0 else s1peer[0]
		
		print "creating string for winner " + winner
		
		if winner[0] == "X":
			winner = p1name
		elif winner[0] == "O":
			winner = p2name
		else:
			winner = "draw"
				
		resultString = "{'game': 'TicTacToe', "\
					"'player1': ['%s', '%s'], "\
					"'player2': ['%s', '%s'], "\
					"'spectator':['%s', '%s'], "\
					"'winner': '%s'}"%(p1name, p1key,p2name,p2key,s1name,s1key,winner)
		
		shaHash = hashlib.sha256(resultString).hexdigest()			
					
		print "Message String created for the game %s"%resultString
		print "SHA256: %s"%shaHash
		return (shaHash, resultString)
		
	
	def gameSummary(self, p1peer, p2peer, s1peer, winner):
		p1key = p1peer[2].publickey if p1peer[2] is not None else self.main.getPublicKey()
		p2key = p2peer[2].publickey if p2peer[2] is not None else self.main.getPublicKey()
		s1key = s1peer[2].publickey if s1peer[2] is not None else self.main.getPublicKey()
		
		scoreJsonHash, scoreJson = self.createScoreFile(p1peer, p2peer, s1peer, winner)
		
		myprivateKey = self.main.rsaKey;

		if p1peer[2] is None:
			#create two ring with both player and sign it and send it to the other two
			ringP1P2 = Ring([p1key, p2key], 2048)
			ringP1S1 = Ring([p1key, s1key], 2048)

			signp1p2 = ringP1P2.sign(scoreJsonHash, myprivateKey);
			signp1s1 = ringP1S1.sign(scoreJsonHash, myprivateKey);

			signs = [{"player1:player2": signp1p2}, {"player1:spectator": signp1s1}]
		
		if p2peer[2] is None:
			ringP1P2 = Ring([p1key, p2key], 2048)
			ringP2S1 = Ring([p2key, s1key], 2048)

			signp1p2 = ringP1P2.sign(scoreJsonHash, myprivateKey);
			signp2s1 = ringP2S1.sign(scoreJsonHash, myprivateKey);

			signs = [{"player1:player2": signp1p2}, {"player2:spectator": signp2s1}]
		
		if s1peer[2] is None:
			ringP1S1 = Ring([p1key, s1key], 2048)
			ringP2S1 = Ring([p2key, s1key], 2048)

			signp1s1 = ringP1S1.sign(scoreJsonHash, myprivateKey);
			signp2s1 = ringP2S1.sign(scoreJsonHash, myprivateKey);

			signs = [{"player1:spectator": signp1s1}, {"player2:spectator": signp2s1}]
	
		self.summary = [{"result": scoreJson,
					"sha256": scoreJsonHash,
					"sign": signs[0]
				},{"result": scoreJson,
					"sha256": scoreJsonHash,
					"sign": signs[1]
				}]
		print ">>>>>>>Summary ready<<<<<<<";
	
		#print "<<Results>>"
		#print summary
		#print
		
		if p1peer[2] is None:
			self.main.sendMulticast("SIGN_RESULT")
			
			signedResults = self.summary
			
			self.main.sendMulticast("RESULT_RING " + json.dumps(signedResults[0]))
			self.main.sendMulticast("RESULT_RING " + json.dumps(signedResults[1]))
		

	def retransmitRings(self):
		for i in range(0, len(self.rings)):
			if i not in self.ringCount:
				self.main.sendMulticast("RESULT_RING " + self.rings[i])
				self.ringCount.append(i)
	
	def validateRings(self, ringContent):
		ring = json.loads(ringContent)
		
		result = ring['result'] 
		sha256 = ring['sha256']
		ringsignature = ring['sign']
		
		testsha256 = hashlib.sha256(result).hexdigest()

		if testsha256 != sha256:
			print "The hashes %s and %s are not equal"%(testsha256,sha256)
			return;
		
		result = json.loads(result.replace("'", "\"").replace("\n", "$"))
		
		p1 = result['player1']
		p2 = result['player2']
		s1 = result['spectator']
		
		p1key = RSA.importKey(p1[1].replace("$", "\n"))
		p2key = RSA.importKey(p2[1].replace("$", "\n"))
		s1key = RSA.importKey(s1[1].replace("$", "\n"))
		
		ringGroupStr = ringsignature.keys()[0]
		
		ringGroup = ringGroupStr.split(":")
		
		if ringGroup[0] == "player1":
			firstkey = p1key;
		elif ringGroup[0] == "player2":
			firstkey = p2key;
		elif ringGroup[0] == "spectator":
			firstkey = s1key
		else:
			print "Signature label unknown: " + ringGroup[1]
		
		if ringGroup[1] == "player1":
			secondkey = p1key;
		elif ringGroup[1] == "player2":
			secondkey = p2key;
		elif ringGroup[1] == "spectator":
			secondkey = s1key
		else:
			print "Signature label unknown: " + ringGroup[1]
			
		testring = Ring([firstkey, secondkey], 2048)
		
		verify = testring.verify(sha256, ringsignature[ringsignature.keys()[0]] )

		if (verify):
			added = False
			for (k, r) in self.validrings:
				if k == ringGroupStr:
					added = True
			
			if not added:
				self.validrings.append((ringGroupStr, ring))
		else:
			print "Ring verification failed "
		
		print str(len(self.validrings)) + " rings verified"
		self.storeifthree()
	
	def storeifthree(self):
		if len(self.validrings) != 3:
			return
	
		signs = []
		for r in self.validrings:
			signs.append(r[1]['sign'])
		
		storeObj = (self.validrings[0][1]['sha256'], json.dumps(self.validrings[0][1]['result']), json.dumps(signs))

		conn = sqlite3.connect("ttts.db")
		cursor = conn.cursor()
		
		cursor.execute("insert into statistics(hash, result, signs) VALUES (?, ?, ?)", storeObj)
		conn.commit()
		self.dbwritten = True;
		
		print "<<<<<Result written to DB>>>>>>>"


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
			self.dbwritten = False;
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
				
				self.gameSummary(self.gameRoom.getPlayer1(), self.gameRoom.getPlayer2(), 
							self.gameRoom.getSpectators()[0], winner)

	
		if "TTTS_MAKE_MOVE" == prefix:
			self.webclient.sendMessage(WebSocketMessage.create("local","TTTS_MAKE_MOVE", ""))
	
		if "SIGN_RESULT" == prefix:
			if self.summary is None:
				print "!!!!Game summary not ready yet!!!!!"
				time.sleep(3)
				self.onPeerMsgReceived(peerIdentity, msg)
				return
			
			signedResults = self.summary
			
			self.main.sendMulticast("RESULT_RING " + json.dumps(signedResults[0]))
			self.main.sendMulticast("RESULT_RING " + json.dumps(signedResults[1]))
			pass
	
		if "RESULT_RING" == prefix:
			ringContent = msgContent.strip()
			if ringContent not in self.rings:
				self.rings.append(ringContent)
				(open("ring" + str(len(self.rings)), "w")).write(ringContent)
				self.validateRings(ringContent)
				
			self.retransmitRings();
	
	
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
				
				self.gameSummary(self.gameRoom.getPlayer1(), self.gameRoom.getPlayer2(), 
							self.gameRoom.getSpectators()[0], winner)
				print "Summary is ready"

			else:
				self.main.sendMulticast("TTTS_MAKE_MOVE")
		
		if "NEW_RSA" == msgPrefix:
			self.main.generateKey() 



		print ">>>>>>"		
		
		
		
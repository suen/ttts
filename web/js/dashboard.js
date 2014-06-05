Dashboard = function(main) {
	
	this.peerListTableNode = $("#peer-list");
	this.stats = null;
	this.main = main
	
	this.peerListTableNode.text("");

	this.addNewPeer = function(peer) {
		
		td = $("<td>").text(peer.substr(peer.indexOf("_")+1));
		td.attr("ref", peer);
		tr = $("<tr>");
		tr.append(td);
		
		td.click(function(evt){
			id_peer = $(this).attr("ref");
			main.showChatBox(id_peer);
		});
		
		this.peerListTableNode.append(tr);
	}
	
	this.erasePeerList = function(peer) {
		this.peerListTableNode.text("");	
	}
	
	this.createNewRoomDOM = function() {
		divcontainer = $("<div>")
		h2 = $("<h2>").text("New Room")
		
		table = $("<table>").attr("class", "table");
		
		tr1 = $("<tr>");
		tr2 = $("<tr>")
		
		td11 = $("<td>").text("Room Name");
		inputName = $("<input>").attr("type", "text");
		td12 = $("<td>").append(inputName);
		
		tr1.append(td11).append(td12);
		
		td21 = $("<td>").attr("colspan", "2");
		createButton = $("<button>").attr("class", "btn btn-primary btn-lg btn-success");
		createButton.text("Create")
		td21.append(createButton);
		
		tr2.append(td21);
		
		table.append(tr1).append(tr2);
		
		divcontainer.append(h2).append(table);
		
		$("#content").append(divcontainer)
		
		that = this
		createButton.click(function(evt) {
			roomName = $(this).parent().parent().prev().children().last().children().val()
			that.main.createRoom(roomName);
		});
	}
	
	this.broadcastReplyTable = null;
	this.createBroadcastReplyDOM = function(){
		divcontainer = $("<div>")
		h2 = $("<h2>").text("Broadcast Reply")
		tablecontainer = $("<div>").attr("class", "broadcast-reply-table-container");
		table = $("<table>").attr("class", "table");

		tablecontainer.append(table)
		
		rebroadcastBtn = $("<button>").text("RE-BROADCAST CREATE ROOM");
		
		rebroadcastBtn.click(function(evt) {
			that.main.reBroadcastLastMessage();
		})
	
		
		this.broadcastReplyTable = table;
		
		divcontainer.append(h2).append(rebroadcastBtn).append(tablecontainer);
		$("#content").html(divcontainer);
	}
	
	this.addNewBroadcastReply = function(msg) {
		d = new Date();
		hour = d.getHours().toString();
		minute = d.getMinutes().toString();
		second = d.getSeconds().toString();
		
		msgde = msg.split(" ")
		peerId = msgde[0]
		roomName = msgde[1]
		
		acceptBtn = $("<button>").attr("class", "btn btn-primary btn-success").attr("ref", roomName + " " + peerId)
		acceptBtn.text("Accept");

		canWatchBtn = $("<button>").attr("class", "btn btn-primary btn-success").attr("ref", roomName + " " + peerId)
		canWatchBtn.text("Can Watch");
		
		dashboard = this
		acceptBtn.click(function() {
			ref = $(this).attr("ref");
			newRoomMsgs = ref.split(" ");
			roomName = newRoomMsgs[0];
			peerId = newRoomMsgs[1];
			dashboard.main.acceptPeer(peerId, roomName);
		});
		
		canWatchBtn.click(function() {
			ref = $(this).attr("ref");
			newRoomMsgs = ref.split(" ");
			roomName = newRoomMsgs[0];
			peerId = newRoomMsgs[1];
			dashboard.main.canWatchPeer(peerId, roomName);
		});
		
		tr = $("<tr>");
		tdtime = $("<td>").text(hour + ":" + minute + ":" + second)
		td = $("<td>").text(msg);
		tdbtn = $("<td>").append(acceptBtn);
		tdbtn2 = $("<td>").append(canWatchBtn);
		tr.append(tdtime)
		tr.append(td).append(tdbtn).append(tdbtn2);
		
		this.broadcastReplyTable.prepend(tr);	
	}
	
	this.joinRoomDOM = function() {
		divcontainer = $("<div>")
		h2 = $("<h2>").text("Join Room")
		h4 = $("<h4>").text("Listening to NEW_GAME broadcast")
		tablecontainer = $("<div>").attr("class", "broadcast-reply-table-container");
		table = $("<table>").attr("class", "table");
		
		this.broadcastReceivedTable = table;
		tablecontainer.append(table)
		divcontainer.append(h2).append(h4).append(tablecontainer);
		$("#content").html(divcontainer);		
	}
	this.broadcastReceivedTable = null;
	this.onNewRoomBroadcastReceived = function(broadcastmsg){
		Logger.log(broadcastmsg);
		console.log(broadcastmsg);
		
		newRoomMsgs = broadcastmsg.split(" ");
		roomName = newRoomMsgs[0];
		peerId = newRoomMsgs[1];
		peerName = peerId.substr(peerId.indexOf("_")+1);
		
		tr = $("<tr>");
		tdtime = $("<td>").text(hour + ":" + minute + ":" + second);
		td = $("<td>").text("Room: " +roomName + " peer: " + peerName);
		
		joinBtn = $("<button>").attr("class", "btn btn-primary btn-success").attr("ref", roomName + " " + peerId)
		joinBtn.text("Join Room");
		
		dashboard = this
		joinBtn.click(function() {
			ref = $(this).attr("ref");
			newRoomMsgs = ref.split(" ");
			roomName = newRoomMsgs[0];
			peerId = newRoomMsgs[1];
			dashboard.main.joinRoom(peerId, roomName);
		});
		
		tdb = $("<td>").append(joinBtn)
		tr.append(tdtime)
		tr.append(td)
		tr.append(tdb)
		
		this.broadcastReceivedTable.prepend(tr);	
	}
	
	this.roomAcceptedDOM = function(roomName, peerId, type) {
		
		if (type == "PLAY") {
			displayText = "You have been accepted to PLAY in '";
		} 
		if (type == "WATCH") {
			displayText = "You have been accepted to WATCH the play in '"
		}
		
		displayText += roomName + "' by '" + peerId + "'"
		
		Logger.log(displayText)
		divcontainer = $("<div>")
		h2 = $("<h2>").text("Join Room")

		divaccepted = $("<div>").attr("class", "small-container");

		startGamebtn = $("<button>").attr("class", "btn btn-primary btn-success").attr("ref", roomName + " " + peerId)
		startGamebtn.text("Start Game");
		divaccepted.append($("<p>").css("text-align", "center")
				.text(displayText)
		)
		divaccepted.append($("<p>").css("text-align", "center").append(startGamebtn));
		
		dashboard = this;
		startGamebtn.click(function(evt) {
			$(this).text("Waiting..")
			$(this).prop('disabled', true);
			dashboard.main.startGame(peerId, roomName)
		});
		
		divcontainer.append(h2).append(divaccepted)
		$("#content").html(divcontainer);		
	}
	
	this.onCanWatch = function(msg) {
		args = msg.split(" ");
		this.roomAcceptedDOM(args[1], args[0], "WATCH")
	}

	this.onAcceptedForRoom = function(msg) {
		args = msg.split(" ");
		this.roomAcceptedDOM(args[1], args[0], "PLAY")
	}
	
	this.createGameDOM = function(msg) {
		Logger.log("now starting the game");
	}

	
//	this.roomAcceptedDOM("hi", "accepted");
	
	//$("#chatbox").hide();
}

Main = function() {

	this.dashboard = new Dashboard(this);
	
	this.onSocketConnect = function() {
		this.connect.sendMessage("PEER_LIST");		
	}
	this.connect = new Connect(this);
	this.onSocketDisconnect = function() {
		$("#thickbox").show();
		$("#thickbox-message").text("Disconnected")
	}
	
	this.chats = [];
	
	this.createChatInstance = function(peerIdentity) {
		chat = new Chat(peerIdentity, this);
		this.chats.push(chat);
		return chat;
	}
	
	this.getChatInstance = function(peerIdentity){
		for (i in this.chats){
			//console.log(this.chats[i].getPeerIdentity() + " == " + peerIdentity)
			if (this.chats[i].getPeerIdentity() == peerIdentity){
				return this.chats[i];
			}
			//Logger.log("no instance found in " + this.chats.size())
		}

		return this.createChatInstance(peerIdentity);
	}
	
	this.showChatBox = function(peerId){
		peerChatIns = this.getChatInstance(peerId);
		peerChatIns.showChatBox()
	}
	
	this.onMessageReceived = function(msg) {
		console.log("Received Msg : " + msg)

		if (msg.substr(0, 19) == "DUPLICATE_WEBCLIENT") {
			$("#thickbox").show();
			$("#thickbox-message").text("Another webclient logged in, Please use your last client")
		}
		
		if (msg.substr(0, 9) == "PEER_LIST") {
			peerList = msg.substr(10);
			console.log(peerList)
			peerObj = JSON.parse(peerList);
			
			this.dashboard.erasePeerList();
			for (i in peerObj) {
				this.dashboard.addNewPeer(peerObj[i]);
			}
			Logger.log("Peer list obtained");
			console.log("Peer list obtained")
			console.log(peerObj)
		};
		
		if (msg.substr(0, 4) == "CHAT") {
			msg = msg.substr(5)
			pIndex = msg.indexOf(" ")
			chatPeer = msg.substr(0, pIndex)
			msg.substr(pIndex+1)
			chatMessage = msg.substr(msg.indexOf(" ")+1)
			
			peerChatIns = this.getChatInstance(chatPeer);
			peerChatIns.onMessageReceived(chatMessage);
		}
		
		if (msg.trim() == "NEW_ROOM BROADCAST DONE") {
			this.dashboard.createBroadcastReplyDOM();
		}
		
		if (msg.substr(0,9) == "JOIN_ROOM") {
			msg = msg.substr(10);
			this.dashboard.addNewBroadcastReply(msg);
		}
		
		if (msg.substr(0,8) == "NEW_ROOM") {
			msg = msg.substr(9)
			this.dashboard.onNewRoomBroadcastReceived(msg);
		}
		
		if (msg.substr(0,12)=="ACCEPTED_FOR") {
			msg = msg.substr(13)
			this.dashboard.onAcceptedForRoom(msg);			
		}
		if (msg.substr(0,9)=="CAN_WATCH") {
			msg = msg.substr(10)
			this.dashboard.onCanWatch(msg);			
		}
		
		this.gameStarted = false;
		if (msg.substr(0,10)=="START_GAME") {
			msg = msg.substr(11)
			if (!this.gameStarted) {
				this.dashboard.createGameDOM(msg);
				this.gameStarted = true;
			} 
			msg = msg.split(" ");
			this.connect.sendMessage("START_OK " + msg[1] + " " + msg[0]);
		}

		if (msg.substr(0,8)=="START_OK") {
			msg = msg.substr(9)
			if (!this.gameStarted) {
				this.dashboard.createGameDOM(msg);
				this.gameStarted = true;
			} 
		}
		
	};
	
	this.sendChat = function(peer, msg) {
		this.connect.sendMessage("CHAT " + peer + " " + msg)
	}
	
	this.createRoom = function(roomName) {
		this.connect.sendMessage("CREATE_ROOM " + roomName);
	}
	
	this.joinRoom = function(peer, roomName) {
		this.connect.sendMessage("JOIN_ROOM " + roomName + " " + peer)
	}
	
	this.acceptPeer = function(peerId, roomName){
		this.connect.sendMessage("ACCEPT_PEER " + roomName + " " + peerId)
	}
	
	this.canWatchPeer = function(peerId, roomName){
		this.connect.sendMessage("CAN_WATCH " + roomName + " " + peerId)
	}
	
	this.startGame = function(peerId, roomName) {
		this.connect.sendMessage("START_GAME " + roomName + " " + peerId)
	}
	
	this.reBroadcastLastMessage = function() {
		this.connect.sendMessage("REANNOUNCE_CREATED_ROOM");
	}
	
	
	this.onPlayerMove = function(move) {
		this.connect.sendMessage("GAME PLAYER_MOVE " + move.toString())
	}
	
	this.send = function() {
		
	}
	
	that = this
	
	$("#broadcast-btn").click(function(evt){ 
		that.connect.sendMessage("BROADCAST")
	});
	
	$("#create-room-form-btn").click(function(evt){ 
		that.dashboard.createNewRoomDOM();
	});

	$("#join-room-btn").click(function(evt){
		that.dashboard.joinRoomDOM();
	});	
	
}

//b = [["X", "O", "X", "", "", ""],["", "", "", "O", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""]]
m = null;
console.log(m)
$(document).ready(function() {
	m = new Main();
	createChatDOM("peer", m)
});


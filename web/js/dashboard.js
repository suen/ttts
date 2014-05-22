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
		$("#thickbox-message").text("O")
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

	};
	
	this.sendChat = function(peer, msg) {
		this.connect.sendMessage("CHAT " + peer + " " + msg)
	}
	
	this.onPlayerMove = function(move) {
		this.connect.sendMessage("GAME PLAYER_MOVE " + move.toString())
	}
	
	this.send = function() {
		
	}
	
	$("#create-room-btn").click(function(evt){ 
		
	});

	$("#join-room-btn").click(function(evt){ 
		
	});	
	
}

//b = [["X", "O", "X", "", "", ""],["", "", "", "O", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""]]
m = null;
console.log(m)
$(document).ready(function() {
	m = new Main();
	createChatDOM("peer", m)
});


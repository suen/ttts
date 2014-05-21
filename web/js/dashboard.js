Dashboard = function() {
	
	this.peerListTableNode = $("#peer-list");
	this.stats = null;
	
	this.peerListTableNode.text("");

	this.addNewPeer = function(peer) {
		
		td = $("<td>").text(peer);
		tr = $("<tr>");
		tr.append(td);
		this.peerListTableNode.append(tr);
	}
	
	this.erasePeerList = function(peer) {
		this.peerListTableNode.text("");	
	}
}

Main = function() {

	this.dashboard = new Dashboard();
	
	this.onSocketConnect = function() {
		this.connect.sendMessage("PEER_LIST");		
	}
	this.connect = new Connect(this);
	this.onSocketDisconnect = function() {
		$("#thickbox").show();
		$("#thickbox-message").text("O")
	}
	
	this.chat = new Chat("suren", this);
	
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
			chatPeer = msg.substr(5, msg.indexOf(" ")-1)
			chatMessage = msg.substr(msg.indexOf(" ")+1)
			this.chat.onMessageReceived(chatMessage)
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

});


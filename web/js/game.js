
Connect = function(listener) {
	this.socket = null;
	this.isopen = false;
	
	this.socket = new WebSocket("ws://127.0.0.1:9000");
	this.socket.binaryType = "arraybuffer";
	this.listener = listener;
	
	this.socket.onopen = function() {
	   console.log("Connected!");
	   isopen = true;
	};

	this.socket.onmessage = function(e) {
	   if (typeof e.data == "string") {
		  //console.log("Text message received: " + e.data);
		  listener.onMessageReceived(e.data);
	   } else {
		  var arr = new Uint8Array(e.data);
		  var hex = '';
		  for (var i = 0; i < arr.length; i++) {
			 hex += ('00' + arr[i].toString(16)).substr(-2);
		  }
		  console.log("Binary message received: " + hex);
	   }
	};
	
	this.socket.onclose = function(e) {
	   console.log("Connection closed.");
	   socket = null;
	   isopen = false;
	};
	
	this.sendMessage = function(msg) {
		this.socket.send(msg);
		console.log("Message sent: " + msg);
	};
	
	console.log("Connection initialized");
}

TicTacToe = function (controller) {
	this.playerChar = "";	
	this.playerClass = "playerC"		
	this.locked = true;
	this.moved = false;
	this.lastmove = [];	
	this.board = [];
	this.controller = controller;
	
	
	$("#confirm-move-btn").click(function(){
		if (this.locked)
			return;
		$(this).text("Wait");
		$(this).addClass("disabled");
	});
	
	this.setPlayerChar = function(playerChar) {
		this.playerChar = playerChar;
	};
	
	this.createBoard = function() {
		for(i=0; i<6; i++) {
			row = [];
			for(j=0; j<6; j++) {
				td_ids = "#" + (i+1).toString() + "-" + (j+1).toString()
				mythis = this
				$(td_ids).click(function(evnt) {
					mythis.boardClickedEvent(this, evnt);
				});
				row.push("");
			}
			this.board.push(row);
		};
		console.log("board initialized");
	};
	
	this.lockBoard = function() {
		this.locked = true;
	};
	
	this.unlockBoard = function() {
		this.locked = false;
		$(this).text("Confirm");
		$(this).removeClass("disabled");
	};

	this.setBoard = function(board) {
		if (typeof(board) == "string") {
			board = board.replace(/\'/g, "\"")
			this.board = JSON.parse(board)
		} else {
			this.board = board;
		}
		this.displayBoard()
	};

	this.getBoard = function() {
		return JSON.stringigy(this.board);
	};
	
	this.write = function(coord) {
		if (this.moved || this.locked)
			return;
		
		this.lastmove = coord;
		this.moved = true;
		
		this.board[coord[0]-1][coord[1]-1] = this.playerChar;
		tdid = "#" + coord[0].toString() + "-" + coord[1].toString();
		//console.log(tdid)
		$(tdid).addClass(this.playerClass);
		$(tdid).text(this.playerChar);
	};

	this.remove = function(coord) {
		if (!this.lastmove[0]==coord[0] || !this.lastmove[1]==coord[1] || this.locked )
			return;
		this.moved = false;
		
		this.board[coord[0]-1][coord[1]-1] = "";
		tdid = "#" + coord[0].toString() + "-" + coord[1].toString()
		$(tdid).removeClass(this.playerClass);
		$(tdid).text("");
	};

	this.displayBoard = function() {
		for(i=0; i<6; i++) {
			row = this.board[i]
			for(j=0; j<6; j++) {
				td_ids = "#" + (i+1).toString() + "-" + (j+1).toString()
				$(td_ids).removeClass("playerA")
				$(td_ids).removeClass("playerB")
				$(td_ids).text(row[j])
				if (row[j]=="X")
					$(td_ids).addClass("playerA")
				if (row[j]=="O")
					$(td_ids).addClass("playerB")
			}
		} 
	}
	
	this.boardClickedEvent = function(obj, evnt) {
		objId = $(obj).attr("id");
		xcord = parseInt(objId.substring(0,1));
		ycord = parseInt(objId.substring(2,3));
		
		if (!evnt.ctrlKey)
			this.write([xcord, ycord]);
		else
			this.remove([xcord, ycord]);
	};



}

Main = function() {
	this.connect = Connect(this);
	this.tic = new TicTacToe(this);
	this.tic.createBoard();
	
	this.onMessageReceived = function(msg) {
		console.log("Received Msg : " + msg)
		msgType = msg.substr(0,4);
		msgContent = msg.substr(5);

		if (msgContent.substr(0, 10) == "PLAYERCHAR") {
			playerChar = msgContent.substr(11, 12);
			this.tic.setPlayerChar(playerChar)
		};
		
		if (msgContent.substr(0,10) == "BOARDSTATE") {
			board = msgContent.substr(11);
			//console.log("Board : " + board)
			board = board.trim();
			this.tic.setBoard(board);
		};
		
		if (msgContent.substr(0, 9) == "YOUR_TURN") {
			this.tic.unlockBoard();
		};
	};
	
	this.onPlayerMove = function(move) {
		this.connect.sendMessage("GAME PLAYER_MOVE " + move.toString())
	}
}

//b = [["X", "O", "X", "", "", ""],["", "", "", "O", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""]]

$(document).ready(function() {
	Main();
});


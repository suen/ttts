
Logger = function(node) {
	this.parentNode = node;
}

Logger.log = function(msg) {
	if (Logger.self == undefined) {
		Logger.self = new Logger($("#network-stream"));
	}
	
	d = new Date();
	hour = d.getHours().toString();
	minute = d.getMinutes().toString();
	second = d.getSeconds().toString();
	
	tr = $("<tr>");
	tdtime = $("<td>").text(hour + ":" + minute + ":" + second)
	td = $("<td>").text(msg);
	tr.append(tdtime)
	tr.append(td)
	Logger.self.parentNode.prepend(tr)
}

Connect = function(listener) {
	this.socket = null;
	this.isopen = false;
	
	this.socket = new WebSocket("ws://127.0.0.1:9000");
	this.listener = listener;
	
	this.socket.onopen = function() {
	   console.log("Connected!");
	   Logger.log("Client connected")
	   console.log(this.socket)
	   isopen = true;
	};

	this.socket.onmessage = function(e) {
		  listener.onMessageReceived(e.data);
	};
	
	this.socket.onclose = function(e) {
	   console.log("Connection closed.");
	   Logger.log("Connection closed")
	   socket = null;
	   isopen = false;
	};
	
	this.sendMessage = function(msg) {
		this.socket.send(msg);
		console.log("Message sent: " + msg);
		Logger.log("Message sent: " + msg);
	};
	
	this.helloworld = function() {
		Logger.log(this.socket);
	};

	console.log("Objects created");
	Logger.log("Objects created");
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
		move = TicTacToe.instance().lastmove
		Logger.log("Sending move " + move)
		move[0]--;
		move[1]--;
		TicTacToe.instance().controller.connect.socket.send("TTTS PLAYER_MOVE " + move.toString());
	});
	
	this.setPlayerChar = function(playerChar) {
		this.playerChar = playerChar;
	};
	
	this.createBoard = function() {
		for(i=0; i<6; i++) {
			row = [];
			for(j=0; j<6; j++) {
				td_ids = "#" + (i+1).toString() + "-" + (j+1).toString()
				$(td_ids).click(function(evnt) {
					TicTacToe.instance().boardClickedEvent(this, evnt);
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
		this.lastmove = [];
		this.moved = false;
		$("#confirm-move-btn").text("Confirm");
		$("#confirm-move-btn").removeClass("disabled");
	};

	this.setBoard = function(board) {
		if (typeof(board) == "string") {
			board = board.replace(/\'/g, "\"")
			newBoard = JSON.parse(board)
		} else {
			newBoard = board;
		}
		if (this.board != newBoard) {
			diff = this.boardDiff(newBoard, this.board)
			if (diff!="")
				Logger.log(diff)
			this.board = newBoard
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
		Logger.log("You moved " + this.lastmove)
	};

	this.remove = function(coord) {
		if (!this.lastmove[0]==coord[0] || !this.lastmove[1]==coord[1] || this.locked )
			return;
		this.moved = false;
		
		this.board[coord[0]-1][coord[1]-1] = "";
		tdid = "#" + coord[0].toString() + "-" + coord[1].toString()
		$(tdid).removeClass(this.playerClass);
		$(tdid).text("");
		Logger.log("Removed " + this.lastmove)
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


	this.boardDiff = function(newBoard, oldBoard) {
		for(i=0; i<6; i++) {
			for(j=0; j<6; j++) {
				if (oldBoard[i][j] != newBoard[i][j]) {
					diff = "(" + (i+1).toString() + "," + (j+1).toString() + ") changed to '" + newBoard[i][j] + "'"
					return diff
				}				
			}

		}
		return "";		
	}

}

TicTacToe.setMain = function(main){
	TicTacToe.main = main;
}

TicTacToe.instance = function() {
	if (typeof(TicTacToe.self) == "undefined")
		TicTacToe.self = new TicTacToe(TicTacToe.main)
	return TicTacToe.self
}

Main = function() {
	this.connect = new Connect(this);
	TicTacToe.setMain(this)
//	this.tic = new TicTacToe(this);
	this.tic = TicTacToe.instance();
	this.tic.createBoard();
	$("#table-container").hide();


	mythis = this
	$("#start-game-button").click(function(evt) {
		mythis.connect.socket.send("TTTS WAITING");
		$("#start-game-button").text("Waiting response");
		$("#start-game-button").addClass("disabled");
	});

	this.onMessageReceived = function(msg) {
		console.log("Received Msg : " + msg)
		msgType = msg.substr(0,4);
		msgContent = msg.substr(5);

		if (msgContent.substr(0, 10) == "START_GAME") {
			playerChar = msgContent.substr(11, 12);
			this.tic.setPlayerChar(playerChar)
			$("#table-container").show();
			$("#game-initialize-container").hide();
			this.tic.unlockBoard()
			
			Logger.log("Game started")
			Logger.log("Player Character is " + playerChar)
		};
		
		if (msgContent.substr(0,11) == "BOARD_STATE") {
			board = msgContent.substr(11);
			//console.log("Board : " + board)
			board = board.trim();
			this.tic.setBoard(board);
			//Logger.log("New board state received")
		};
		
		if (msgContent.substr(0, 9) == "MAKE_MOVE") {
			Logger.log("Your turn")
			this.tic.unlockBoard();
		};
		
		if (msgContent.substr(0,9) == "GAME_OVER") {
			player_winner = msgContent.substr(17,18)
			Logger.log("Player " + player_winner + " wins, GAME OVER")
		};
	};
	
	this.onPlayerMove = function(move) {
		this.connect.sendMessage("GAME PLAYER_MOVE " + move.toString())
	}
}

//b = [["X", "O", "X", "", "", ""],["", "", "", "O", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""]]

$(document).ready(function() {
	m = Main();
});


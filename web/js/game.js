
TicTacToe = function (playerChar) {
	this.playerChar = "X";	
	this.playerClass = "playerC"		
	this.locked = true;
	this.moved = false;
	this.lastmove = [];	
	this.board = [];
	
	$("#confirm-move-btn").click(function(){
		$(this).text("Wait");
		$(this).addClass("disabled");
	});
	
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

	this.setBoard = function(board) {
		this.board = board;
		this.displayBoard()
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

	this.getBoard = function() {
		return this.board;
	}

}

b = [["X", "O", "X", "", "", ""],["", "", "", "O", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""],["", "", "", "", "", ""]]

game = new TicTacToe()
game.createBoard()



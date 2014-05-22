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



function createChatDOM(peer, evntListener) {

	
}

Chat = function(peer, main) {
	chatbox = $("<div>");
	chatbox.attr("class", "chatbox");
	winHeight = window.innerHeight;
	winWidth = window.width;
	chatTopMargin = winHeight - 300;
	chatBoxCount = main.chats.length;
	chatbox.css("margin-top", chatTopMargin.toString() + "px")
	chatbox.css("margin-left", ((chatBoxCount*210)+100).toString() +"px")
	
	chatboxTitle = $("<div>")
	chatboxTitle.attr("class", "title")
	
	chatboxh4 = $("<h4>");
	chatboxh4.text("Chat - " + peer.substr(peer.indexOf("_")+1));
	
	closeButton = $("<button>")
	closeButton.attr("class", "control")
	closeButton.text("X")
	
	minimizeButton = $("<button>")
	minimizeButton.attr("class", "control")
	minimizeButton.text("-")
	
	minimizeButton.click(function() {
		mychatStream = $(this).parent().next();
		mychatInput = mychatStream.next();
		mychatbox = mychatStream.parent();
		
		display = mychatStream.css("display")
		
		if (display.toLowerCase()!="none"){
			mychatStream.hide();
			mychatInput.hide();
			mychatbox.css("height", "40px")
			mychatbox.css("margin-top", (winHeight-40).toString() + "px")
		} else {
			mychatStream.show();
			mychatInput.show();
			mychatbox.css("height", "300px")
			mychatbox.css("margin-top",chatTopMargin.toString() + "px")
		}
			
	});


	closeButton.click(function(){
		mychatbox = $(this).parent().parent();
		display = mychatbox.css("display")
		if(display.toLowerCase()!="none") {
			mychatbox.hide();
		}
	});

	chatboxTitle.append(chatboxh4);
	chatboxTitle.append(closeButton);
	chatboxTitle.append(minimizeButton);
	
	chatStream = $("<div>");
	chatStream.attr("class", "chat-stream")
	
	chatInput = $("<div>");
	chatInput.attr("class", "chat-input")
	
	chatText = $("<input>");
	chatText.attr("type", "text")
	sendButton = $("<button>")
	sendButton.text("send");
	
	chatInput.append(chatText)
	chatInput.append(sendButton)
	
	chatbox.append(chatboxTitle)
	chatbox.append(chatStream)
	chatbox.append(chatInput)
	
	$("body").prepend(chatbox);	
	chatbox.hide();
	
	this.getPeerIdentity = function() {
		return peer;
	}
	
	this.onMessageReceived = function(chatmsg) {
		p = $("<p>").text(peer.substr(peer.indexOf("_")+1) + ": " + chatmsg);
		chatStream.append(p)

		display = chatbox.css("display")
		if(display.toLowerCase()=="none") {
			chatbox.show();
			this.chatBoxHidden = false;
		}
	};
	
	this.chatbox = chatbox
	
	this.showChatBox = function() {
		console.log("showing box")
		display = this.chatbox.css("display")
		console.log(display)
		if(display.toLowerCase()=="none") {
			this.chatbox.show();
		}	
	}
	
	sendButton.click(function(evt) { 
		
		txtField = $(this).prev();
		chatmsg = txtField.val();
		txtField.val("");
		
//		chatmsg = chatText.val();
//		chatText.val("");

		p = $("<p>").text("Me: " + chatmsg);
		
		myChatStream = $(this).parent().prev()
		
		myChatStream.append(p)
		main.sendChat(peer, chatmsg)
	});

		
	chatbox.show();
	Logger.log("new Chat instance for " + peer + " created")
}


Connect = function(listener) {
	this.socket = null;
	this.isopen = false;
	
	this.socket = new WebSocket("ws://127.0.0.1:9000");
	this.listener = listener;
	
	this.socket.onopen = function() {
	   Logger.log("Websocket connected")
	   isopen = true;
	   listener.onSocketConnect();
	};

	this.socket.onmessage = function(e) {
		listener.onMessageReceived(e.data);
	};
	
	this.socket.onclose = function(e) {
	   Logger.log("Connection closed")
	   socket = null;
	   isopen = false;
	   listener.onSocketDisconnect()
	};
	
	
	this.sendMessage = function(msg) {
		this.socket.send(msg);
		console.log("Message sent: " + msg);
		Logger.log("Message sent: " + msg);
	};
	
	this.helloworld = function() {
		Logger.log(this.socket);
	};

	Logger.log("Connect initializing");
}

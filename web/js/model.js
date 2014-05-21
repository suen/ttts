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


Chat = function(peer, main) {
	this.parentNode = $("#chatbox")
	winHeight = window.innerHeight;
	winWidth = window.width;
	chatTopMargin = winHeight - 300;
	this.parentNode.css("margin", chatTopMargin.toString() + "px 0px 0px 100px")

	$("#chatbox-title").text("Chat - " + peer)
	$("#chat-stream").text("")
	$("#chat-text").text("")

	
	this.onMessageReceived = function(chatmsg) {
		p = $("<p>").text(peer + ": " + chatmsg);
		$("#chat-stream").append(p)		
	};
	
	
	chat = this
	$("#chat-send").click(function() {
		chatmsg = $("#chat-text").val()
		$("#chat-text").val("")
		p = $("<p>").text("Me: " + chatmsg);
		$("#chat-stream").append(p)
		main.sendChat(peer, chatmsg)
	});
	
	
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

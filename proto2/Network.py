
from twisted.internet.protocol import DatagramProtocol, Factory,ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.error import CannotListenError
from twisted.internet import reactor
from twisted.python import log
import time
from socket import SOL_SOCKET, SO_BROADCAST
from threading import Thread
from patterns import Singleton
from Game import TicTacToe
from Player import AI,AsyncPlayer

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory
                                       
class UDPBroadcaster(DatagramProtocol):
    
    def __init__(self, address, breceiver):
        self.broadcastAddress = address
        self.breceiver = breceiver
        self.broadcastMsg = ""
        self.defaultMsg = ""
        self.broadcastCount = 0
        self.startBroadcast = False
    
    def setMsgToBroadcast(self, message):
        self.broadcastMsg = message
        self.broadcastCount = 3
        self.startBroadcast = True
        print "UDP broadcast started"
    
    def setDefaultBroadcastMessage(self, message):
        self.defaultMsg = message
        
    def doDefaultBroadcast(self):
        self.broadcastCount = 3
        self.broadcastMsg = self.defaultMsg if self.defaultMsg !="" else "BROADCAST";
        self.startBroadcast = True
        print "UDP default broadcast started"
    
    def stopBroadcast(self):
        self.startBroadcast = False
        self.broadcastCount = 0
        self.broadcastMsg = ""
        print "UDP broadcast stopped" 
        
    def startProtocol(self):
        self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
        Thread(target=self.doInfiniteBroadcast).start()
        print "UDP protocol initiated, ready for broadcast" 
    
    def doInfiniteBroadcast(self):
        while 1:
            if self.startBroadcast:
                self.transport.write(self.broadcastMsg, self.broadcastAddress)
                self.broadcastCount -= 1
                if self.broadcastCount == 0:
                    self.startBroadcast = False
                    self.broadcastMsg = ""
            time.sleep(2)
 

    def datagramReceived(self, datagram, address):
        if datagram == self.broadcastMsg:
            return
        print 'Datagram received: ', repr(datagram)
        self.breceiver.onBroadcastReceived((datagram, address))

    def getBroadcastListener(self):
        pass


class MyTCPProtocol(LineReceiver):
    def __init__(self):
        self.peerName = ""

    def connectionMade(self):
        self.sendLine("CONNECT " + Network.Instance().main.username)
        pass

    def connectionLost(self, reason):
        print "Peer disconnected"
        Network.Instance().removePeer(self)

    def onLineReceived(self, peerIdentity, line):
        print "No TCP Listeners implemented for msg by " + peerIdentity + " >>> " + line
        pass
    
    def lineReceived(self, line):       
        print "TCP received: " + line
        
        if "CONNECT " in line:         
            space_index = line.find(" ")    
            peerName = line[space_index+1:]
            if len(peerName) > 30:
                return
            
            if peerName == Network.Instance().main.username:
                return
            
            #peerCount = len(Network.Instance().getPeers())
            
            #self.peerName = str(peerCount) + "_" + peerName
            
            Network.Instance().addPeer(peerName, self)
            #self.sendLine("welcome '" + peerName + "', You have been added to my list. There are currently " 
            #              + str(peerCount) + " in my list, Welcome abroad")
            self.sendLine("CONNECT_OK " + Network.Instance().main.username)
        
        elif "CONNECT_OK" in line:
            space_index = line.find(" ")
            peerName = line[space_index+1:]
            if len(peerName) > 30:
                return
            
            #peerCount = len(Network.Instance().getPeers())
            #self.peerName = str(peerCount) + "_" + peerName
            Network.Instance().addPeer(peerName, self)            
        else:
            self.onLineReceived(self.peerName, line);
            

class MyTCPProtocolFactory(Factory):
    
    def buildProtocol(self, addr):
        return MyTCPProtocol()
        
    
class MyWebSocketServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        Network.Instance().setWebClient(self)

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
            self.sendMessage(payload, isBinary)
            return
        msg = payload.decode('utf8')
        #Network.Instance().treat(self, msg)
        #self.sendMessage(msg, isBinary)
        print("Text message received: {0}".format(payload.decode('utf8')))
        print("NOBODY IS LISTENING TO THIS MESSAGE ????")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        Network.Instance().removeWebClient(self)


@Singleton
class Network:
    
    def __init__(self):
        self.broadcastReceiver = None
        self.broadcaster = None
        self.websocketFactory = None
        self.peers = []
    
    def setMain(self, main):
        self.main = main

    def setWebClient(self, webclient):
        self.main.setWebClient(webclient)
           
    def removeWebClient(self, webclient):
        self.setWebClient(webclient)

    def addPeer(self, name, peer):        
        for (n,p,ip) in self.peers:
            if p == peer:
                return
        peerCount = len(self.getPeers())
        peer.peerName = str(peerCount)+ "_" + name
        peer.ip = peer.transport.getPeer().host
        peer.onLineReceived = self.main.onPeerMsgReceived
        self.peers.append((peer.peerName, peer, peer.transport.getPeer().host))
        print "new peer"+ str((peer.peerName, peer.transport.getPeer().host))
        self.main.onPeerListChange()

    def removePeer(self, peer):
        print "Remove Peer initialized"
        for (n, p, ip) in self.peers:
            if p == peer:
                self.peers.remove((n, p, ip))
                print("peer removed " + str((n, ip)))
                self.main.onPeerListChange()
    
    def getPeerByIP(self, ip):
        for (n, p, i) in self.peers:
            if i == ip:
                return p
        return None

    def getPeerById(self, id):
        for (n, p, i) in self.peers:
            if n == id:
                return p
        return None
    
    def getPeers(self):
        return self.peers
    
    def setBroadcastAddress(self, broadcastAddress):
        self.broadcastAddress = broadcastAddress;
    
    def setUDPPort(self, udpPort):
        self.udpPort = udpPort;
        
    def setTCPPort(self, tcpPort):
        self.tcpPort = tcpPort;
        
    def setWebSocketPort(self, wsocketPort):
        self.wsocketPort = wsocketPort
            
    def startNetwork(self):
        try:
            self.broadcaster = UDPBroadcaster((self.broadcastAddress, self.udpPort), self)
            reactor.listenUDP(self.udpPort, self.broadcaster)
    
            self.websocketFactory = WebSocketServerFactory("ws://localhost:" + str(self.wsocketPort), debug = False)
            self.websocketFactory.protocol = MyWebSocketServerProtocol 
            reactor.listenTCP(self.wsocketPort,self.websocketFactory)
            
            reactor.listenTCP(self.tcpPort, MyTCPProtocolFactory())
    
            self.clientFactory = ClientFactory();
            self.clientFactory.protocol = MyTCPProtocol
        
            reactor.run()
        except CannotListenError:
            print "Cannot listen to " + str(self.udpPort) + " or " + str(self.tcpPort) + " .. exiting "

    

    def connectPeer(self, address, port):
        reactor.connectTCP(address, port, self.clientFactory);

    def treat(self, peer, msg):
        print msg
        self.main.onWebPeerMessage(peer, msg)
        #return str(len(self.webclient)) + " peers connected"
        
    #UDP broadcast
    def broadcast(self):
        self.broadcaster.doDefaultBroadcast()
    
    def stopBroadcast(self):
        self.broadcaster.stopBroadcast()
    
    def onBroadcastReceived(self, dtuple):
        datagram,peerIdentity = dtuple;
        
        broadcastingPeer = self.getPeerByIP(peerIdentity[0])

        if broadcastingPeer is None:
            self.connectPeer(peerIdentity[0], peerIdentity[1]);
            #return
        #self.main.onBroadcastReceived(dtuple);
        #print dtuple, " RECEIVED"
    
    def sendMulticast(self, msg):
        for (n,p,ip) in self.peers:
            p.sendLine(msg)


class BroadcastListener():

    def __init__(self, main):
        self.main = main

    def onBroadcastReceived(self, dtuple):
        self.main.broadcastReceived(dtuple)
    
    
#from twisted.internet import reactor
#from twisted.internet.protocol import Protocol, ClientFactory
import Socket
from Event import Event

# Possible client states
STATE_DISCONNECTED = "STATE_DISCONNECTED"
STATE_CONNECTING = "STATE_CONNECTING"
STATE_CONNECTED = "STATE_CONNECTED"

# Reason codes for status changes
REASON_USER = "REASON_USER"
REASON_CONNECTION_LOST = "REASON_CONNECTION_LOST"
REASON_CONNECTION_FAILED = "REASON_CONNECTION_FAILED"

class Connection:
	"""The component that handles managing the connection to the TA server."""
	
	def __init__(self):
		self._state = STATE_DISCONNECTED
		self._proto = None
		self._host = None
		self._port = None
		self._socket = None
		self.stateChanged = Event()
		self.dataReceived = Event()
		self.callback = lambda:None
		self._sockets = []
		
	def connect(self, host, port):
		"""Start connecting to a given host/port, terminating current connection if necessary."""
		if not self.isDisconnected():
			self.disconnect()
		self._host = host
		self._port = port
		#reactor.connectTCP(host, port, self)
		self._socket = TiberiaSocket(self)
		self._socket.callback = self.callback
		self._sockets.append(self._socket)
		self._socket.connect(host,port)
		self._enterState(STATE_CONNECTING)
			
	def disconnect(self):
		"""Disconnect from the current server if connected."""
		if not self.isDisconnected():
			# TODO: make this not warn if you cancel during a connection
			#self._proto.transport.loseConnection()
			self._socket.close()
			self._enterDisconnectedState()
		
	def getHost(self):
		return self._host
		
	def getPort(self):
		return self._port
		
	def getState(self):
		return self._state
		
	def isDisconnected(self):
		return self._state == STATE_DISCONNECTED
		
	def isConnecting(self):
		return self._state == STATE_CONNECTING
		
	def isConnected(self):
		return self._state == STATE_CONNECTED
			
	def sendRaw(self, data):
		"""Send byte data to the server."""
		if self.isConnected():
			self._socket.send(data)
		
	def _enterDisconnectedState(self, reason=REASON_USER):
		self._proto = None
		self._host = None
		self._port = None
		self._socket = None
		self._enterState(STATE_DISCONNECTED, reason)
			
	def _enterState(self, state, reason=None):
		oldState = self._state
		self._state = state
		if state != oldState:
			self.stateChanged.notify(state, reason)
		
	def _disconnected(self, sock):
		if sock is self._socket:
			self._enterDisconnectedState(REASON_CONNECTION_LOST)

	def _connectionFailed(self, sock):
		if sock is self._socket:
			self._enterDisconnectedState(REASON_CONNECTION_FAILED)

	def _connected(self, sock):
		if sock is self._socket:
			self._enterState(STATE_CONNECTED)
		
	def _dataReceived(self, sock, data):
		if sock is self._socket:
			self.dataReceived.notify(data)
			
	def update(self):
		#print 'Connection.update()'
		socketDied = False
		for s in self._sockets:
			s.update()
			if s.state == Socket.ST_DISCONNECTED:
				socketDied = True
		if socketDied:
			self._sockets = [x for x in self._sockets if x.state != Socket.ST_DISCONNECTED]
					
			
class TiberiaSocket(Socket.Socket):
	def __init__(self, conn):
		Socket.Socket.__init__(self)
		self._conn = conn

	def connectionFailed(self):
		self._conn._connectionFailed(self)
		
	def connected(self):
		self._conn._connected(self)
		
	def disconnected(self):
		self._conn._disconnected(self)
		
	def dataReceived(self, data):
		self._conn._dataReceived(self, data)

__all__ = ['Connection',
			'STATE_DISCONNECTED',
			'STATE_CONNECTING',
			'STATE_CONNECTED',
			'REASON_USER',
			'REASON_CONNECTION_LOST',
			'REASON_CONNECTION_FAILED'
			]
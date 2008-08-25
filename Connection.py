from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory

# Possible client states
STATE_DISCONNECTED = "STATE_DISCONNECTED"
STATE_CONNECTING = "STATE_CONNECTING"
STATE_CONNECTED = "STATE_CONNECTED"

# Reason codes for status changes
REASON_USER = "REASON_USER"
REASON_CONNECTION_LOST = "REASON_CONNECTION_LOST"
REASON_CONNECTION_FAILED = "REASON_CONNECTION_FAILED"

class Connection(ClientFactory):
	"""The component that handles managing the connection to the TA server."""
	
	def __init__(self, client):
		self._client = client
		self._state = STATE_DISCONNECTED
		self._proto = None
		self._host = None
		self._port = None
		
	def connect(self, host, port):
		"""Start connecting to a given host/port, terminating current connection if necessary."""
		if not self.isDisconnected():
			self.disconnect()
		self._host = host
		self._port = port
		reactor.connectTCP(host, port, self)
		self._enterState(STATE_CONNECTING)
			
	def disconnect(self):
		"""Disconnect from the current server if connected."""
		if not self.isDisconnected():
			self._proto.loseConnection()
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
			self._proto.transport.write(data)
		
	def _enterDisconnectedState(self, reason=REASON_USER):
		self._proto = None
		self._host = None
		self._port = None
		self._enterState(STATE_DISCONNECTED, reason)
			
	def clientConnectionLost(self, connector, reason):
		self._enterDisconnectedState(REASON_CONNECTION_LOST)

	def clientConnectionFailed(self, connector, reason):
		self._enterDisconnectedState(REASON_CONNECTION_FAILED)

	def buildProtocol(self, addr):
		self._proto = TwistedConnection(self)
		self._enterState(STATE_CONNECTED)
		return self.conn
			
	def _enterState(self, state, reason=None):
		self._state = state
		self._client.notify('conn.stateChanged', state, reason)
		# TODO: Other events for specific stuff like connect/disconnect...?
		
	def _dataReceived(self, data):
		self._client.notify('conn.dataReceived', data)	

class TwistedConnection(Protocol):
	def __init__(self, conn):
		self._conn = conn

	def dataReceived(self, data):
		self._conn._dataReceived(data)

__all__ = ['Client',
			'STATE_DISCONNECTED',
			'STATE_CONNECTING',
			'STATE_CONNECTED',
			'REASON_USER',
			'REASON_CONNECTION_LOST',
			'REASON_CONNECTION_FAILED'
			]
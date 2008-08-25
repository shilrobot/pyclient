from ClientCore import *
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
import Config

# Possible client states
STATE_DISCONNECTED = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2

# TODO: Clean up updateUI() stuff? - onConnectionStateChanged might be better
class TwistedClient(ClientCore, ClientFactory):
	'Part of the client that actually connects to the interweb using Twisted.'

	def __init__(self):
		ClientCore.__init__(self)
		# TODO: ClientFactory.__init__? Don't think so
		self.conn = None
		self.state = STATE_DISCONNECTED

		# Register commands
		self.registerCommand(['connect', 'open'], self.connect, '[host] [port]',
							 'Connects to a remote host. ip:port notation is also supported.')
		self.registerCommand(['disconnect', 'close'], self.disconnect, None,
							 'Closes an active connection.')
		self.registerCommand(['send', 'say'], self.send, '<text>',
								'Sends a line of text. Equivalent to not using any command.')


	def connect(self, event=None):
		if isinstance(event, str) and event != '':
			self.echo("Connect with params not configured yet :(")
		if self.state == STATE_DISCONNECTED: 
			reactor.connectTCP(Config.getStr('server/host'),
								Config.getInt('server/port'),
								self)
			self.echo('Connecting...')
			self._enterState(STATE_CONNECTING)
		pass

	def disconnect(self, event=None):
		if self.state == STATE_CONNECTED:
			self.conn.transport.loseConnection()
			self.state = STATE_DISCONNECTED
			self.conn = None
		pass

	def send(self, text=None):
		# TODO: Split up into lines
		lines = text.splitlines()
		together = ''
		for l in lines:
			if self.state != STATE_CONNECTED:
				self.echo("Can't send line, not connected: "+l)
			else:
				together += l+"\r\n"
		if self.state == STATE_CONNECTED:
			self.conn.transport.write(together)

	# Twisted stuff
	#def startedConnecting(self, connector):
	#	self.echo('Connecting...')
	#	self.updateUI()

	def clientConnectionLost(self, connector, reason):
		self.state = STATE_DISCONNECTED
		self.conn = None
		self.echo('Connection lost')
		self._enterState(STATE_DISCONNECTED)

	def clientConnectionFailed(self, connector, reason):
		self.conn = None
		self.echo('Connection failed')
		self._enterState(STATE_DISCONNECTED)

	def buildProtocol(self, addr):
		self.echo('Connected')
		self.conn = ActiveConnection(self)
		self._enterState(STATE_CONNECTED)
		return self.conn


	def _enterState(self, state):
		self.state = state
		self.stateChanged(state)

	# Stuff that gets overridden by actual GUI clients...
	def onReceiveText(self, data):
		"""Called when data is received."""
		pass
	
	def stateChanged(self, newstate):
		"""Called when the connection state changes."""
		pass

class ActiveConnection(Protocol):
	def __init__(self, parent):
		self.parent = parent

	def dataReceived(self, data):
		self.parent.onReceiveText(data)

__all__ = ['TwistedClient',
			'STATE_DISCONNECTED',
			'STATE_CONNECTING',
			'STATE_CONNECTED']

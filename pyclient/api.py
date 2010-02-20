"""Public pyclient API."""

from pyclient.Client import Client
from pyclient.Connection import STATE_CONNECTED
import types


# yes this is on purpose
import ta2.Constants
from ta2.Constants import *

_client = Client.instance

class ClientAPI:
	"""
	This is a facade to simplify interacting with PyClient.
	Please use a ClientAPI object instead of accessing other classes/modules in pyclient.
	"""

	
	def echo(self, line=''):
		"""Prints a line to the output window."""
		_client.echo(line)
	
	def connect(self, host=None, port=None):
		"""Tells the client to connect to a particular server."""
		_client.connect(host, port)
		
	def disconnect(self):
		"""Kills the connection, if there is one. No effect if there is no connection."""
		_client.conn.disconnect()
				
	isConnected = property(lambda: _client.conn.getState() == STATE_CONNECTED)
				
	host = property(lambda: _client.conn.getHost())
		
	port = property(lambda: _client.conn.getPort())
		
	def send(self, line):
		"""Sends data to the server if connected."""
		_client.send(line)
		
	def execute(self, line):
		"""Executes a command as if the user had typed it in the input box."""
		_client.execute(self, line)
	
	def hasConfigKey(self, key):
		"""Checks if a configuration key exists."""
		return _client.cfg.hasKey(key)
		
	def getConfigBool(self, key, default=False):
		"""Gets a configuration value coerced to a boolean value."""
		return _client.cfg.getBool(key, default)
		
	def getConfigInt(self, key, default=0):
		"""Gets a configuration value coerced to an integer."""
		return _client.cfg.getConfigInt(key, default)
		
	def getConfigStr(self, key, default=''):
		"""Gets a configuration value as a string."""
		return _client.cfg.getConfigStr(key, default)
		
	def setConfigBool(self, key, value):
		"""Sets a configuration value to a boolean option."""
		_client.cfg.setBool(key, value)
		
	def setConfigInt(self, key, value):
		"""Sets a configuration value to an integer."""
		_client.cfgsetConfigInt(key, value)
		
	def setConfigStr(self, key, value):	
		"""Sets a configuration value to a string."""
		_client.cfg.setConfigStr(key, value)
	
	def saveConfig(self):
		"""Saves the current configuration to file. Useful for saving changes made to settings."""
		_client.saveConfig()
	
	def addCommand(self, name_or_names, func, params='', doc=''):
		"""Registers a command with the client core."""
		_client.addCommand(name_or_names, func, params, doc)
	
	def command(self, f, params='', doc=None):
		"""Decorator to simplify calling addCommand."""
		assert isinstance(f, types.FunctionType)
		if doc is None:
			if hasattr(f, '__doc__'):
				doc = f.__doc__
			else:
				doc = ''
		self.addCommand(f.func_name, f, params, doc)
		return f
			
	def addHook(self, name, func):
		"""Registers an event hook with the client core."""
		if name == 'lineReceived':
			_client.lineReceived.register(func)
		elif name == 'xmlReceived':
			_client.xmlReceived.register(func)
		elif name == 'connected':
			_client.connected.register(func)
		elif name == 'disconnected':
			_client.disconnected.register(func)
		else:
			assert False
	
	def hook(self, name):
		"""Decorator to simplify calling addHook."""
		def _helper(f):
			self.addHook(name,f)
			return f
		return _helper

__all__ = [
	'ClientAPI'
]

# Add color codes, etc. from ta2 constants. Only require one import this way.
for x in dir(ta2.Constants):
	if x.startswith('EV_') or x.startswith('ANSI_'):
		__all__.append(x)

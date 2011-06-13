"""Public pyclient API."""

from pyclient.Client import Client
from pyclient.Connection import STATE_CONNECTED
import types
import inspect
import re

MODNAME_REGEX = re.compile("^plugins\.(\w+)?")

# yes this is on purpose
import ta2.Constants
from ta2.Constants import *

_client = Client.instance

class ClientAPI:
	"""
	This is a facade to simplify interacting with PyClient.
	Please use a ClientAPI object instead of accessing other classes/modules in pyclient.
	"""

	def __init__(self, plugname=None):
		if plugname is None:
			# MAGIC PLUGIN NAME DETECTION
			# Only include the module directly under 'plugins'
			caller = inspect.stack()[1]
			calling_module = inspect.getmodule(caller[0])
			match = MODNAME_REGEX.match(calling_module.__name__)
			assert match is not None
			self._plugname = match.group()
		else:
			self._plugname = 'plugins.'+plugname
	
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
			
	def _config(self):
		return _client.cfg.setdefault(self._plugname,{})
		
	config = property(_config)
	
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

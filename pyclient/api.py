"""Public pyclient API."""

from pyclient.Client import Client
from pyclient.Connection import STATE_CONNECTED
import types
import inspect
import re

MODNAME_REGEX = re.compile("^plugins\.(\w+)?")

_client = Client.instance
	
def magic_deco(deco_func):
	"""
	Makes it easier to define decorators that can be used with and without parameter lists.
	
	Works like this:
	
	class C:
		@magic_deco
		def foo(self, f, ...):
			...
	
	@C.foo applied to g ---> g = C.foo(g)
	@C.foo(*args, **kwargs) applied to g ---> g = C.foo(g, *args, **kwargs)
	"""
	def helper(self, *args, **kwargs):
		if len(args) == 1 and kwargs == {} and inspect.isroutine(args[0]):
			return deco_func(self, args[0])
		else:
			def helper2(f):
				return deco_func(self, f, *args, **kwargs)
			return helper2
	return helper

class ClientAPI:
	"""
	This is a facade to simplify interacting with PyClient.
	"""

	def __init__(self, plugname):
		self._plugname = plugname
	
	def echo(self, line=''):
		"""Prints a line to the output window."""
		_client.echo(line)
	
	def connect(self, host=None, port=None):
		"""Tells the client to connect to a particular server."""
		_client.connect(host, port)
		
	def disconnect(self):
		"""Kills the connection, if there is one. No effect if there is no connection."""
		_client.conn.disconnect()
				
	@property
	def isConnected(self):
		return _client.conn.getState() == STATE_CONNECTED
		
	@property
	def host(self):
		return _client.conn.getHost()
		
	@property
	def port(self):
		return _client.conn.getPort()
		
	def send(self, line):
		"""Sends data to the server if connected."""
		_client.send(line)
		
	def execute(self, line):
		"""Executes a command as if the user had typed it in the input box."""
		_client.execute(self, line)
			
	@property
	def config(self):
		return _client.cfg.setdefault(self._plugname,{})
		
	@config.setter
	def _setConfig(self, config):
		_client.cfg[self._plugname] = config
	
	def saveConfig(self):
		"""Saves the current configuration to file. Useful for saving changes made to settings."""
		_client.saveConfig()
	
	def addCommand(self, name_or_names, func, params='', doc=''):
		"""Registers a command with the client core."""
		_client.addCommand(name_or_names, func, params, doc)
	
	@magic_deco
	def command(self, f, params='', doc=None, aliases=[]):
		if doc is None:
			if hasattr(f, '__doc__'):
				doc = f.__doc__
			else:
				doc = ''
		self.addCommand([f.func_name] + aliases, f, params, doc)
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
	
	@magic_deco
	def hook(self, f, name):
		"""Decorator to simplify calling addHook."""
		self.addHook(name, f)
		return f
		
	@property
	def name(self):
		return "PyClient"
		
	@property
	def version(self):
		# TODO
		return None

def getClient(plugname=None):
	"""Returns a facade for plugins to use"""
	
	if plugname is None:
		# MAGIC PLUGIN NAME DETECTION
		# Only include the module directly under 'plugins'
		caller = inspect.stack()[1]
		calling_module = inspect.getmodule(caller[0])
		match = MODNAME_REGEX.match(calling_module.__name__)
		assert match is not None
		final_plugname = match.group()
	else:
		final_plugname = 'plugins.'+plugname
	
	return ClientAPI(final_plugname)

__all__ = [
	'getClient'
]

# Add color codes, etc. from ta2 constants. Only require one import this way.
import ta2.Constants
for name,val in ta2.Constants.__dict__.items():
	if name.startswith('EV_') or name.startswith('ANSI_'):
		globals()[name] = val
		__all__.append(name)
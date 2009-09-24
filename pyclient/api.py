"""Facade to simplify interfacing with Pyclient."""

from pyclient.Client import *
from pyclient.Connection import *
import types

# yes this is on purpose
import ta2.Constants
from ta2.Constants import *

__all__ = [
	'echo',
	'connect',
	'disconnect',
	'isConnected',
	'getHost',
	'getPort',
	'send',
	'execute',
	'hasConfigKey',
	'getConfigBool',
	'getConfigInt',
	'getConfigStr',
	'setConfigBool',
	'setConfigInt',
	'setConfigStr',
	'saveConfig',
	'addCommand',
	'command',
	'addHook',
	'hook'
]
	
# Add color codes, etc. from ta2 constants. Only require one import this way.
for x in dir(ta2.Constants):
	if x.startswith('EV_') or x.startswith('ANSI_'):
		__all__.append(x)

_client = Client.instance

def echo(line=''):
	_client.echo(line)

def connect(host=None, port=None):
	_client.connect(host, port)
	
def disconnect():
	_client.conn.disconnect()
	
def isConnected():
	return _client.conn.getState() == STATE_CONNECTED
	
def getHost():
	return _client.conn.getHost()
	
def getPort():
	return _client.conn.getPort()
	
def send(line):
	_client.send(line)
	
def execute(line):
	_client.execute(line)

def hasConfigKey(key):
	return _client.cfg.hasKey(key)
	
def getConfigBool(key, default=False):
	return _client.cfg.getBool(key, default)
	
def getConfigInt(key, default=0):
	return _client.cfg.getConfigInt(key, default)
	
def getConfigStr(key, default=''):
	return _client.cfg.getConfigStr(key, default)
	
def setConfigBool(key, value):
	_client.cfg.setBool(key, value)
	
def setConfigInt(key, value):
	_client.cfgsetConfigInt(key, value)
	
def setConfigStr(key, value):
	_client.cfg.setConfigStr(key, value)

def saveConfig():
	_client.saveConfig()

def addCommand(name_or_names, func, params='', doc=''):
	_client.addCommand(name_or_names, func, params, doc)

# this is a decorator
def command(f, params='', doc=None):
	assert isinstance(f, types.FunctionType)
	if doc is None:
		if hasattr(f, '__doc__'):
			doc = f.__doc__
		else:
			doc = ''
	addCommand(f.func_name, f, params, doc)
	return f

if 0:
	class command:
		def __init__(self, params='', doc=None):
			self.params = params
			self.doc = doc
			
		def __call__(self,f):
			assert isinstance(f, types.FunctionType)
			doc = self.doc
			if doc is None:
				if hasattr(f, '__doc__'):
					doc = f.__doc__
				else:
					doc = ''
			addCommand(f.func_name, f, self.params, doc)
			return f
		
# TODO: Make this a decorator?
def addHook(name, func):
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

def hook(name):
	def _helper(f):
		addHook(name,f)
		return f
	return _helper
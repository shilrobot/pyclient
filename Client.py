import os
import Config
import Connection
import GTKClient
import Commands

class Client:
	"""Root object for the whole client. Its central responsibilities are managing
	the other core components (configuration, connection, interpreter, GUI, etc.)
	and maintaining the central extension point registry, which is used by
	the plugin system and for event notification in general.
	
	Important variables:
	.conn - Connection
	.cfg - Config
	(TODO: More)
	
	The way the extension point system works is this. The Client object
	maintains what is basically a dictionary that maps string names
	to lists of arbitrary objects. This can be used to register commands,
	toolbar buttons, configuration GUI pages, etc. It can also be used
	to notify others of signals.
	
	The plugin system provides wrappers around these that can be used
	to automatically unregister anything the plugin registered, to allow
	clean plugin installation/removal at runtime.
	
	Special signals: When a new extension is registered, two signals are sent out:
	1) client.registered(key, value)
	2) client.registered:<keyName>(value)
	
	The same thing occurs when you unregister an extension, except replace
	'registered' with 'unregistered'.
	
	The two versions are so you can narrow down to modifications to just one
	extension key to improve performance, or look at all extension keys if
	that's what you need to do.	
	
	Extension names generally use camelCase words separated by dots.
	The first word is usually the name of the module or plugin the extension
	is related ot.
	"""
	
	def __init__(self):
		self._registry = {}
		self._initConfig()
		self.conn = Connection.Connection(self)
		self.cmds = Commands.Commands(self)
		pass
		
	# TODO: Remove 'Config.currentConfig' entirely and have it only exist under Client
	def _initConfig(self):
		"""Initializes the config object."""
		# Initialize configuration.
		# Put config XML file in the pyclient directory
		self._configPath = \
			os.path.abspath(os.path.join(os.path.dirname(__file__),'pyclient-config.xml'))
		self.cfg = Config.currentConfig
		if os.path.exists(self._configPath):
			self.cfg.loadXML(self._configPath)
		else:
			print "%s doesn't exist, using default settings" % (self._configPath)		
				
	def run(self):
		"""Performs the main loop of the client."""
	
		# Run stuff...
		# TODO: Clean this up as more stuff folds into the new design
		from GTKClient import GTKClient
		gtkClient = GTKClient(self)
		
		from twisted.internet import reactor
		reactor.run()
		
	def shutdown(self):
		"""Closes down the client."""
		self.conn.disconnect()
		self.cfg.saveXML(self._configPath)
		
	def register(self, key, value):
		"""Registers an extension.
		More than one value can exist under a certain key, and values can exist twice."""
		key = str(key)
		self._registry.setdefault(key, []).append(value)
		self.notify('client.registered', key, value)
		self.notify('client.registered:'+key, value)
		
	def unregister(self, key, value):
		"""Unregisters a single extension."""
		key = str(key)
		if self._registry.has_key(key):
			self._registry[key].remove(value)
			self.notify('client.unregistered', key, value)
			self.notify('client.unregistered:'+key, value)

	def getExtensions(self, key):
		"""Returns the extensions registered under a certain key, if any."""
		return self._registry.get(key, [])
		
	def getExtensionKeys(self):
		"""Returns an unsorted list of extension keys that have children."""
		return self._registry.keys()
		
	def notify(self, key, *args, **kwargs):
		"""Calls all extensions under a certain key with the given parameters."""
		for ext in self.getExtensions(key):
			ext(*args, **kwargs)
		
	def echo(self, line):
		self.notify('client.echo', line)
		
	def send(self, line):
		# TODO: Send through output filter stack...
		if self.conn.state == Connection.STATE_CONNECTED:
			self.conn.sendRaw(line+'\r\n')
		else:
			self.echo("Can't send, not connected: "+line)
			
	def execute(self, line):
		self.cmds.execute(line)

	

"""Configuration system."""

from pyclient.core import Component, ExtensionPoint, Interface
from pyclient.profile import Profile

class ConfigVal(object):
	"""A descriptor that acts like a normal attribute, but actually pulls
	its value from the configuration system."""
	
	def __init__(self, section, key, default=None):
		self._section = section
		self._key = key
		self._default = default
		
	def __get__(self, inst, owner):
		# Read from Config. Use the default value supplied in our
		# constructor if it can't find the key.
		return Config().get(self._section, self._key, self._default)
		
	def __set__(self, inst, val):
		# Write to Config
		Config().set(self._section, self._key, val)

# TODO: Typed things like ConfigVal, for numbers, bools, strings, lists, etc.?
		
class IConfigListener(Interface):
	"""Interface that listens for changes in the configuration."""
	
	def onConfigChanged(self, section, key, oldval, newval):
		"""Called when a configuration value is changed.
		@param section Config section name.
		@param key Config key name.
		@param oldval Value of the key before it was changed, or None.
		@param newval Value of the key after being changed.
		"""
		pass
		
class Config(Component):
	"""The configuration system component."""

	listeners = ExtensionPoint('IConfigListener')

	def initComponent(self):
		self._sections = {}
		
	def has(self, section, key):
		return (self._sections.has_key(section) and
					self._sections[section].has_key(key))
		
	def get(self, section, key, default=None):
		if self._sections.has_key(section):
			sec = self._sections[section]
			if sec.has_key(key):
				return sec[key]
		return default
		
	def set(self, section, key, val):
		if self._sections.has_key(section):
			sec = self._sections[section]
		else:
			sec = {}
			self._sections[section] = sec
		oldval = sec.get(key, None)
		sec[key] = val
		for L in self.listeners:
			L.onConfigChanged(section, key, oldval, val)
		
	def getConfigPath(self):
		return Profile().getPath('pyclient.cfg')
		
	def loadConfig(self):
		cfgpath = self.getConfigPath()
		try:
			f = open(cfgpath, 'rt')
		except:
			print 'Cannot load config file: %s' % cfgpath
			return
		currSec = None
		for line in f.readlines():
			line = line.strip()
			if len(line) == 0 or line.startswith('#') or line.startswith('//'):
				continue
			elif line.startswith('[') and line.endswith(']'):
				currSec = line[1:-1]
			elif currSec is not None and line.find('=') >= 1:
				index = line.find('=')
				keyName = line[:index].strip()
				value = line[index+1:].strip()
				#print '%s,%s' % (repr(keyName), repr(value))
				self.set(currSec, keyName, value)
			else:
				print 'Unparseable config line: %s' % line
				pass
		f.close()
		
	def saveConfig(self):
		# TODO
		pass
		
__all__ = ['Config', 'ConfigVal', 'IConfigListener']



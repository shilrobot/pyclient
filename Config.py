"""Configuration system for PyClient."""

import xml.etree.ElementTree as ET
	
class Config:
	"""Holds the actual config values. Really a glorified dictionary."""
	
	def __init__(self):
		# TODO: Move away from having defaults here like this
		self._defaults = {
			'input/font': 'monospace 10',
			'output/font': 'monospace 10',
			'output/fg/default': '#EEEEEE',
			'output/fg/0': '#000000',
			'output/fg/1': '#FF0000',
			'output/fg/2': '#00FF00',
			'output/fg/3': '#FFFF00',
			'output/fg/4': '#0000FF',
			'output/fg/5': '#FF00FF',
			'output/fg/6': '#00FFFF',
			'output/fg/7': '#FFFFFF',
			'output/bg/default': '#000000',
			'output/urls': '#0000FF',
			'output/gtk24wrapping': True,
			'server/host': 'tiberia.homeip.net',
			'server/port': 1337,
			'ui/sizeX': 700,
			'ui/sizeY': 500,
		}
		self.reset()
		
	def getBool(self, name, default=False):
		try:
			val = self._config[name].lower()
			if val in ['1','true','on','yes','enable','why not']:
				return True
			else:
				return False
		except:
			return default
			
	def hasKey(self, name):
		return self._config.has_key(name)
			
	def getInt(self, name, default=0):
		try:
			return int(self._config[name])
		except:
			return default
			
	def getStr(self, name, default=''):
		try:
			return str(self._config[name])
		except:
			return default
		
	def setBool(self, name, val):
		self._config[name] = ['False','True'][val]
		
	def setStr(self, name, val):
		self._config[name] = val
		
	def setInt(self, name, val):
		self._config[name] = val

	def load(self, filename):
		tree = ET.parse(filename)
		root = tree.getroot()
		if root.tag != 'pyclient-config':
			print "Error loading config: Invalid XML root element tag: "+root.tag
			return
		for keytag in root.getiterator('key'):
			if keytag.attrib.has_key('name') and keytag.attrib.has_key('value'):
				self._config[keytag.attrib['name']] = keytag.attrib['value']
				
	def save(self, file):
		keys = self._config.keys()
		keys.sort()
		root = ET.Element('pyclient-config')
		root.text = "\n  "
		for k in keys:
			subelem = ET.SubElement(root, 'key', name=k, value=str(self._config[k]))
			if k is not keys[-1]:
				subelem.tail = "\n  "
			else:
				subelem.tail = "\n"
		ET.ElementTree(root).write(file, encoding='UTF-8')
		
	def reset(self):
		"""Resets to defaults."""
		self._config = self._defaults.copy()
		

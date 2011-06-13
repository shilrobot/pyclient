"""Configuration system for PyClient."""

try:
	import json
except:
	import simplejson as json
	
DEFAULTS = {
	'input/font': 'monospace 10',
	'output/font': 'monospace 10',
	'output/fg/default': '#EEEEEE',
	'output/fg/colors': [
		'#000000',
		'#FF0000',
		'#00FF00',
		'#FFFF00',
		'#0000FF',
		'#FF00FF',
		'#00FFFF',
		'#FFFFFF'
	],
	'output/bg/default': '#000000',
	'output/urls': '#0000FF',
	'server/host': 'tiberia.homeip.net',
	'server/port': 1337,
	'ui/size': [700,500]
}
	
class Config(dict):
	
	def __init__(self):
		self._reset()

	def load(self, filename):
		"""Loads from the given filename in JSON format, returning a boolean indicating success"""
		self._reset()
		try:
			with open(filename) as f:
				self.update(json.load(f))
			return True
		except Exception, e:
			print 'Config.load: %s: %s' % (filename, e)
			return False
				
	def save(self, filename):
		"""Saves to the given filename in JSON format, returning a boolean indicating success"""
		try:
			with open(filename, "w") as f:
				json.dump(self, f, indent=2)
			return True
		except Exception, e:
			print 'Config.load: %s: %s' % (filename, e)
			return False
		
	def _reset(self):
		"""Resets to defaults."""
		self.clear()
		self.update(DEFAULTS)

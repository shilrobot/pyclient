"""Global (ick) configuration system for PyClient."""
import pickle

class ConfigSettings:
	"""Holds the actual config values. Really a glorified dictionary."""
	
	def __init__(self):
		# TODO: It seems weird to have these in here, like this...
		# 		violation of some kind of something-something...
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
			'connection/autologin': False,
			'connection/username': '',
			'connection/password': '', # TODO: base64?
			'connection/advprotomode': 'off', # 'off', 'initial', 'afterlogin'
			'ui/size': (700,500),
			'ui/pos': None,
			'ui/panePos': None,
		}
		self.reset()

	def get(self, name, default=None):
		return self._config.get(name, default)
		
	def set(self, name, value):
		self._config[name] = value

	def save(self, file):
		"""Saves config to a file."""
		if isinstance(file, str):
			file = open(file, "w")
		pickle.dump(self._config, file)
		
	def load(self, file):
		"""Loads config from a file."""
		if isinstance(file, str):
			file = open(file, "r")
		newconfig = pickle.load(file)
		self._config = self._defaults.copy()
		self._config.update(newconfig)
		
	def reset(self):
		"""Resets to defaults."""
		self._config = self._defaults.copy()
		

# Global config 'singleton'
currentConfig = ConfigSettings()
#currentConfig.save('wtf')

# Quick access to config settings
get = currentConfig.get
set = currentConfig.set

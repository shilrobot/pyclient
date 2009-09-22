

class EventSource:
	def __init__(self):
		self._registry = {}
		
	def register(self, key, value):
		self._registry.setdefault(key, []).append(value)
		
	def unregister(self, key, value):
		if self._registry.has_key(key):
			self._registry[key].remove(value)
			
	def notify(self, key, *args, **kwargs):
		"""Calls all extensions under a certain key with the given parameters."""
		for ext in self.getHandlers(key):
			ext(*args, **kwargs)
			
	def getHandlers(self, key):
		"""Returns the extensions registered under a certain key, if any."""
		return self._registry.get(key, [])
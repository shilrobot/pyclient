

class Event:
	def __init__(self):
		self.handlers = []
		
	def register(self, value):
		self.handlers.append(value)
		
	def unregister(self, value):
		self.handlers.remove(value)
		
	def notify(self, *args, **kwargs):
		for handler in self.handlers:
			handler(*args, **kwargs)
			
	def notifyCancelable(self, *args, **kwargs):
		"""Executes all handlers, stopping if one returns True and returning True. Otherwise executes the rest and returns False."""
		for handler in self.handlers:
			if handler(*args, **kwargs):
				return True
		return False

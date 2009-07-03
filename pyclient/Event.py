

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

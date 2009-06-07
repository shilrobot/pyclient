# TODO: I think this can probably all go in Client... blah.
import re

class Command:
	def __init__(self, names, func, params='', doc=''):
		self.names = [s.lower() for s in names]
		self.func = func
		self.params = params
		self.doc = doc

COMMAND_REGEX = re.compile(r'^/([a-zA-Z0-9_-]+)([ \t](.*))?$')
		
class Commands:
	"""Implements the interpreter that lines are sent through before
	getting transmitted to the server, to handle command execution
	and so on."""
	
	def __init__(self, client):
		self._client = client
		self._gatherCommands()
		self._client.register('client.registered:commands', self._onCommandsChanged)
		self._client.register('client.unregistered:commands', self._onCommandsChanged)
		# TODO: Register default commands
		
	def _gatherCommands(self):
		self._cmds = {}
		for cmd in self._client.getExtensions('commands'):
			# Register all names for the command if it's not already been done
			# TODO: Warn for multiply defined commands, or commands with
			#       with missing attributes, etc...
			for name in cmd.names:
				if not self._cmds.has_key(name):
					self._cmds[name] = cmd
		
	def _onCommandsChanged(self, key, val):
		# Just totally redo command list for now
		# TODO: Smart caching system
		self._gatherCommands()
		
	def execute(self, line):
		match = COMMAND_REGEX.match(line)
		if match is not None:
			commandName = match.group(1).lower()
			parameters = match.group(3)
			if self._cmds.has_key(commandName):
				command = self._cmds[commandName]
				command.func(parameters)
			else:
				self._client.echo('Unknown command: /'+match.group(1))
		else:
			# TODO
			self._client.send(line)

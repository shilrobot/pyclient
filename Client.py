import os
import Config
import Connection
import GTKClient
import Commands
import EventBus
import re
from ta2 import *
import gtk
import twisted.copyright
import sys
import Version

class Command:
	def __init__(self, names, func, params=None, doc=None):
		if isinstance(names, str):
			self.names = [names.lower()]
		else:
			self.names = [s.lower() for s in names]
		if params is None:
			params = ''
		if doc is None:
			doc = ''
		self.func = func
		self.params = params
		self.doc = doc

COMMAND_REGEX = re.compile(r'^/([a-zA-Z0-9_-]+)([ \t](.*))?$')

class Client:
	
	def __init__(self):
		self._commands = {}
		#self.events = EventBus.EventBus()
		self.conn = Connection.Connection()
		self.conn.dataReceived.register(self._onDataReceived)
		# TODO: Remove 'Config.currentConfig' entirely and have it only exist under Client
		self._configPath = \
			os.path.abspath(os.path.join(os.path.dirname(__file__),'config.xml'))
		self.cfg = Config.currentConfig
		if os.path.exists(self._configPath):
			self.cfg.loadXML(self._configPath)
		self.addCommand(["connect","open"], self._cmdConnect, '[host [port]]', 'Connects to server. host:port format is also allowed.')
		self.addCommand(["disconnect","close"], self._cmdClose, '', 'Disconnects from server.')
		self.addCommand("echo", self._cmdEcho, '<text>', 'Displays a line of text in the output window.')
		self.addCommand("version", self._cmdVersion, '[all]', 'Displays version information. Follow with "all" to send.')
		self.addCommand("colors", self._cmdColors, '', 'Shows available color codes.')
		self.addCommand("me", self._cmdMe, '<test>', 'Emulation of IRC /me command.')
		self.addCommand("help", self._cmdHelp, '', 'Displays help information.')
		#self.addCommand("eval", _cmdMe)
		#else:
		#	print "%s doesn't exist, using default settings" % (self._configPath)		
		pass	
				
	def run(self):
		"""Performs the main loop of the client."""
	
		# Run stuff...
		# TODO: Clean this up as more stuff folds into the new design
		from GTKClient import GTKClient
		self.ui = GTKClient(self)
		
		self.echo(EV_GREEN+EV_BOLD+Version.FULLNAME)
		self.echo(EV_NORMAL+EV_CYAN+'See /help for a list of commands')
		self.echo(EV_NORMAL)
		
		from twisted.internet import reactor
		reactor.run()
		
	def shutdown(self):
		"""Closes down the client."""
		self.conn.disconnect()
		self.cfg.saveXML(self._configPath)
		
	def echo(self, line=None):
		if line is None:
			line = ''
		self.ui.onReceiveText(ANSI_NORMAL+line+'\r\n')
		
	def send(self, line):
		# TODO: Send through output filter stack...
		if self.conn.getState() == Connection.STATE_CONNECTED:
			self.conn.sendRaw(line+'\r\n')
		else:
			self.echo("Can't send, not connected: "+line)
			
	def execute(self, line):
		match = COMMAND_REGEX.match(line)
		if match is not None:
			commandName = match.group(1).lower()
			parameters = match.group(3)
			if self._commands.has_key(commandName):
				command = self._commands[commandName]
				print "parameters="+repr(parameters)
				if parameters is None:
					parameters = ''
				command.func(parameters)
			else:
				self.echo('Unknown command: /'+match.group(1))
		else:
			# TODO
			self.send(line)

	def addCommand(self, names, func, params='', doc=''):
		cmd = Command(names, func, params, doc)
		for n in cmd.names:
			self._commands[n] = cmd
		
	def _onDataReceived(self, data):
		self.ui.onReceiveText(data)
			
	def _cmdConnect(self, params):
		host = self.cfg.getStr('server/host', 'tiberia.homeip.net')
		port = self.cfg.getInt('server/port', '1337')
		self.conn.connect(host,port)
		
	def _cmdClose(self, params):
		self.conn.disconnect()
		
	def _cmdEcho(self, params):
		self.echo(params)
				
	def _cmdColors(self, parms):
		# TODO: Clean this up some
		self.echo("Basic TA color codes:")
		self.echo("\x1b[0m"  +   "<-0>  Default      \x1b[1m     <-1> Bold")
		self.echo("\x1b[0m\x1b[31m<-31> Red          \x1b[1m<-31><-1> Bold Red")
		self.echo("\x1b[0m\x1b[32m<-32> Green        \x1b[1m<-32><-1> Bold Green")
		self.echo("\x1b[0m\x1b[33m<-33> Yellow       \x1b[1m<-33><-1> Bold Yellow")
		self.echo("\x1b[0m\x1b[34m<-34> Blue         \x1b[1m<-34><-1> Bold Blue")
		self.echo("\x1b[0m\x1b[35m<-35> Magenta      \x1b[1m<-35><-1> Bold Magenta")
		self.echo("\x1b[0m\x1b[36m<-36> Cyan         \x1b[1m<-36><-1> Bold Cyan")
		self.echo("\x1b[0m\x1b[37m<-37> White        \x1b[1m<-37><-1> Bold White")
		self.echo("Extended TA2 codes:")
		self.echo(EV_B+"<-b>Bold<-/b>      "+EV_NORMAL+EV_S+"<-s>Strikethrough<-/s>"+EV_NORMAL)
		self.echo(EV_I+"<-i>Italic<-/i>    "+EV_NORMAL+EV_SETCOLOR+"ff8800<-cFF8800>Color</-c>"+EV_NORMAL)
		self.echo(EV_U+"<-u>Underline<-/u>"+EV_NORMAL)
		
	def _cmdMe(self, parms):
		self.send('.action '+parms)
		
	def _cmdVersion(self, parms):
		# Process python version info
		pyver = sys.version
		pyver = pyver[:pyver.find(' ')]
		func = self.echo
		if parms.strip() == 'all': func=self.send
		# TODO: PyGTK version
		func('PyClient '+Version.VERSION + \
			 ' / Python '+pyver + \
			 ' / GTK '+ '.'.join([str(x) for x in gtk.gtk_version]) + \
			 ' / PyGTK '+ '.'.join([str(x) for x in gtk.pygtk_version]) + \
			 ' / Twisted '+twisted.copyright.version)
			 
	def _cmdHelp(self, parms=None):
		#self.echo("PyClient commands are executed by preceding their name with a forward slash. To send a literal forward slash at the beginning of a line, type two forward slashes.")
		#self.echo("PyClient supports the following commands:")
		self.echo()
		cmds = []
		for c in self._commands.values():
			if not c in cmds:
				cmds.append(c)
		#cmds = self._commands.items()
		cmds.sort(lambda a,b:cmp(a.names[0], b.names[0]))
		for c in cmds:
			tabs = "    "
			self.echo(EV_BOLD+EV_WHITE+"/"+c.names[0]+" "+c.params+EV_NORMAL)
			self.echo(tabs+c.doc)
			if len(c.names) > 1:
				s = tabs+"Aliases: "+EV_BOLD + ", ".join(["/"+x for x in c.names[1:]])+EV_NORMAL
				self.echo(s)
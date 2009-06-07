import os
import Config
import Connection
import GTKClient
#import Commands
import EventBus
import re
from ta2 import *
import gtk
import twisted.copyright
import sys
import Version
import Log
import difflib

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
		
# Levenshtein edit distance implementation by bbands from comp.lang.python
# see http://groups.google.com/group/comp.lang.python/browse_frm/thread/43f3ef0bf88f40d2
def distance(a,b):
    c = {}
    n = len(a); m = len(b)

    for i in range(0,n+1):
        c[i,0] = i
    for j in range(0,m+1):
        c[0,j] = j

    for i in range(1,n+1):
        for j in range(1,m+1):
            x = c[i-1,j]+1
            y = c[i,j-1]+1
            if a[i-1] == b[j-1]:
                z = c[i-1,j-1]
            else:
                z = c[i-1,j-1]+1
            c[i,j] = min(x,y,z)
    return c[n,m] 
    
def relative(a, b):
    """
    Computes a relative distance between two strings. Its in the range
    (0-1] where 1 means total equality.
    @type a: string
    @param a: arg one
    @type b: string
    @param b: arg two
    @rtype: float
    @return: the distance
    """
    d = distance(a,b)
    longer = float(max((len(a), len(b))))
    shorter = float(min((len(a), len(b))))    
    r = ((longer - d) / longer) * (shorter / longer)
    return r 
    
COMMAND_REGEX = re.compile(r'^/([a-zA-Z0-9_-]+)([ \t](.*))?$')

class Client:
	
	def __init__(self):
		self._commands = {}
		#self.events = EventBus.EventBus()
		self.conn = Connection.Connection()
		self.conn.dataReceived.register(self._onDataReceived)
		self.conn.stateChanged.register(self._onConnStateChanged)
		self.log = Log.Log(self)
		# TODO: Remove 'Config.currentConfig' entirely and have it only exist under Client
		self._configPath = self.getPath('config.xml')
		self.cfg = Config.Config()
		if os.path.exists(self._configPath):
			self.cfg.load(self._configPath)
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
		
	def getPath(self, relpath):
		return os.path.abspath(os.path.join(os.path.dirname(__file__), relpath))
				
	def run(self):
		"""Performs the main loop of the client."""
	
		# Run stuff...
		# TODO: Clean this up as more stuff folds into the new design
		from GTKClient import GTKClient
		self.ui = GTKClient(self)
		
		self.echo(EV_GREEN+EV_BOLD+Version.FULLNAME)
		self.echo(EV_CYAN+'See /help for a list of commands')
		self.echo()
		
		from twisted.internet import reactor
		reactor.run()
		
	def shutdown(self):
		"""Closes down the client."""
		self.conn.disconnect()
		self.cfg.save(self._configPath)
		
	def echo(self, line=None):
		if line is None:
			line = ''
		self._displayText(ANSI_NORMAL+line+ANSI_NORMAL+'\r\n')
		
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
				if parameters is None:
					parameters = ''
				command.func(parameters)
			else:
				self.echo('Unknown command: /%s %s' % (match.group(1), self._suggestCommands(match.group(1))))
		else:
			# TODO
			self.send(line)

	def addCommand(self, names, func, params='', doc=''):
		cmd = Command(names, func, params, doc)
		for n in cmd.names:
			self._commands[n] = cmd
		
	def _onDataReceived(self, data):
		self._displayText(data)
		
	def _displayText(self, data):
		self.log.write(data)
		self.ui.onReceiveText(data)		
		
	def _onConnStateChanged(self, state, reason):
		if state == Connection.STATE_CONNECTING:
			self.echo('Connecting to %s:%d...' % ( self.conn.getHost(), self.conn.getPort()))
		elif state == Connection.STATE_CONNECTED:
			self.echo('Connected!')
			self.cfg.setStr('server/host', self.conn.getHost())
			self.cfg.setInt('server/port', self.conn.getPort())
		elif state == Connection.STATE_DISCONNECTED:
			if reason == Connection.REASON_CONNECTION_FAILED:
				self.echo('Connection failed')
			else:
				self.echo('Connection closed')
		self.ui.stateChanged(state)
				
		
	def _cmdConnect(self, params):
		if len(params.strip()) > 0:
			match = re.match("^\s*([^:\s]+)\s*:?\s*([0-9]+)?\s*$", params)
			if match is not None:
				host = match.group(1)
				port = match.group(2)
				if port is None:
					port = 23 # telnet
				else:
					port = int(port)
			else:
				self.echo("Malformed host/port spec: %s" % params)
				return
		else:
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
		self.echo(EV_B+"<-b>Bold<-/b>      "+EV_NORMAL+EV_S+"<-s>Strikethrough<-/s>")
		self.echo(EV_I+"<-i>Italic<-/i>    "+EV_NORMAL+EV_SETCOLOR+"ff8800<-cFF8800>Color</-c>")
		self.echo(EV_U+"<-u>Underline<-/u>")
		
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
			 
	def _showCommandHelp(self, c):
		tabs = "    "
		self.echo(EV_BOLD+EV_WHITE+"/"+c.names[0]+" "+c.params)
		self.echo(tabs+c.doc)
		if len(c.names) > 1:
			s = tabs+"Aliases: "+EV_BOLD + ", ".join(["/"+x for x in c.names[1:]])
			self.echo(s)
			
	def _suggestCommands(self, enteredName):
		enteredName = enteredName.lower()
		closest = difflib.get_close_matches(enteredName, self._commands.keys(), 4, .7)
		if len(closest) == 0:
			best = None
			bestLen = -1
			for c in self._commands.keys():
				if c.startswith(enteredName):
					if best is None or len(c) < bestLen:
						best = c
						bestLen = len(c)
			if best is not None:
				closest = [best]
		if len(closest) == 0:
			return ''
		elif len(closest) == 1:
			return "(Did you mean /%s?)" % closest[0]
		else:
			return "(Did you mean %s or /%s?)" % (', '.join(["/"+x for x in closest[:-1]]), closest[-1])
						 
	def _cmdHelp(self, parms=None):
		args = parms.strip().split()
		if len(args) > 0:
			cmdname = args[0].lower()
			if cmdname in self._commands:
				self._showCommandHelp(self._commands[cmdname])
			else:
				self.echo("Unknown command: /%s %s" % (args[0], self._suggestCommands(args[0])))
		else:
			self.echo()
			cmds = []
			for c in self._commands.values():
				if not c in cmds:
					cmds.append(c)
			cmds.sort(lambda a,b:cmp(a.names[0], b.names[0]))
			for c in cmds:
				self._showCommandHelp(c)
				

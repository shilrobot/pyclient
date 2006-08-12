import sys
#import wx # for version info
from ta2 import *
import Version

# For version information
import gtk
import twisted.copyright


class ClientCore(object):
	'Central client interpreter, unrelated to specific connection or UI scheme.'
	
	def __init__(self):
		self.commands = []
		self.commandDict = {}

		self.registerCommand('help', self.help, '[command name]',
								'Displays help information.')
		self.registerCommand(['echo', 'print'], self.echo, '<text>',
								'Displays text in the output area.')
		self.registerCommand('version', self.version, None,
								'Sends version information.')
		self.registerCommand('me', self.me, '<text>',
								'Emulation of IRC /me for TA; sends .action <text>')
		self.registerCommand('eval', self.eval, '<expr>',
								'Evaluates a Python expression and displays the result.')
		self.registerCommand('colors', self.colors, None, 
								'Displays colorcode examples')
		self._evalScope = {'client':self}

	def startupBanner(self):
		self.echo(EV_GREEN+EV_BOLD+Version.FULLNAME)
		self.echo(EV_NORMAL+EV_CYAN+'See /help for a list of commands')
		self.echo(EV_NORMAL)

	def interpret(self, text):	
		'Executes a line in the interpreter.'
		if text.startswith('//'):
			self.send(text[1:])
		elif text.startswith('/'):
			n = text.find(' ', 1)
			if n == -1:
				n = len(text)
			cmd = text[1:n]
			cmd = cmd.lower()
			cmdObj = self.commandDict.get(cmd, None)
			if cmdObj != None:
				cmdObj.func(text[n:].lstrip()) # TODO: Meh
			else:
				self.echo("Unknown command '"+cmd+"'. See /help for list of commands.")
		else:
			self.send(text)  

	def registerCommand(self, names, *args):
		'Adds a command to the list of registered commands.'
		if not isinstance(names, list):
			names = [names]		
		cmd = RegisteredCommand(names, *args)
		self.commands.append(cmd)
		for n in names:
			self.commandDict[n] = cmd

	def colors(self, parms=None):
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
	
	def help(self, parms=None):
		self.echo("PyClient commands are executed by preceding their name with a forward slash. To send a literal forward slash at the beginning of a line, type two forward slashes.")
		self.echo("PyClient supports the following commands:")
		self.echo()
		cmds = self.commands[:] # copy slice
		cmds.sort(lambda a,b:cmp(a.names[0], b.names[0]))
		for c in cmds:
			tabs = "    "
			self.echo(EV_BOLD+EV_WHITE+"/"+c.names[0]+" "+c.params+EV_NORMAL)
			self.echo(tabs+c.doc)
			if len(c.names) > 1:
				s = tabs+"Aliases: "+EV_BOLD + ", ".join(["/"+x for x in c.names[1:]])+EV_NORMAL
				self.echo(s)

	def version(self, parms=None):
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

	def me(self, parms=''):
		self.send('.action '+parms)

	def eval(self, parms=''):
		# TODO: Refactor this shit fo' real, yo.
		# 		This needs a lot more attention in general...
		func = self.echo
		parms = parms.strip()
		if parms == 'all' or parms.startswith('all '):
			func = self.send
			parms = parms[len('all'):].strip()
		elif parms == 'reset' or parms.startswith('reset '):
			self._evalScope = {'client':self} # TODO: Duplication
			return
		# TODO: Print the eval part afterwards, so if we switch send() it works right?
		func('>>> '+parms)
		if parms.strip() == '' or parms.lstrip().startswith('#'):
			return
		import StringIO
		fakestdout = StringIO.StringIO()
		oldstdout = sys.stdout
		sys.stdout = fakestdout
			
		try:
			#func(repr(eval(parms)))
			code = compile(parms+'\n', '<user input>', 'single')
			exec code in self._evalScope
			func(fakestdout.getvalue())
		except:
			# TODO: Don't show full traceback in all mode?
			func(fakestdout.getvalue())
			sys.stdout = oldstdout
			import traceback
			func(traceback.format_exc())
		sys.stdout = oldstdout

	def echo(self, text=''):
		self.onReceiveText(ANSI_NORMAL+text+'\r\n')

	# Should be overridden
	def send(self, param=''): pass
	def onReceiveText(self, text): pass

# Info about a command
class RegisteredCommand:
	def __init__(self, names, func, params=None, doc=''):
		self.names = [n.lower() for n in names]
		self.func = func
		if params == None:
			params = ''
		self.params = params
		self.doc = doc



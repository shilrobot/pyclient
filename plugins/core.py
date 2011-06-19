from pyclient.api import *
import re

client = getClient()

@client.command
def colors(line):
	"""Shows available color codes."""
	client.echo("Basic TA color codes:")
	client.echo(ANSI_NORMAL+"<-0>  Default      "+ANSI_BOLD+"     <-1> Bold")
	client.echo(ANSI_RED+   "<-31> Red          "+ANSI_BOLD+"<-31><-1> Bold Red")
	client.echo(ANSI_GREEN+ "<-32> Green        "+ANSI_BOLD+"<-32><-1> Bold Green")
	client.echo(ANSI_YELLOW+"<-33> Yellow       "+ANSI_BOLD+"<-33><-1> Bold Yellow")
	client.echo(ANSI_BLUE+  "<-34> Blue         "+ANSI_BOLD+"<-34><-1> Bold Blue")
	client.echo(ANSI_PINK+  "<-35> Magenta      "+ANSI_BOLD+"<-35><-1> Bold Magenta")
	client.echo(ANSI_CYAN+  "<-36> Cyan         "+ANSI_BOLD+"<-36><-1> Bold Cyan")
	client.echo(ANSI_WHITE+ "<-37> White        "+ANSI_BOLD+"<-37><-1> Bold White")
	client.echo("Extended TA2 codes:")
	client.echo(EV_B+"<-b>Bold<-/b>      "+EV_NORMAL+EV_S+"<-s>Strikethrough<-/s>")
	client.echo(EV_I+"<-i>Italic<-/i>    "+EV_NORMAL+EV_SETCOLOR+"ff8800<-cFF8800>Color</-c>")
	client.echo(EV_U+"<-u>Underline<-/u>")

@client.command(params="<text>")
def echo(line):
	"""Displays a line of text in the output window."""
	client.echo(line)
	
@client.command(aliases=['close'])
def disconnect(line):
	"""Instructs the client to disconnect from the server."""
	client.disconnect()
	
@client.command(params="<text>")
def me(line):
	"""Emulation of IRC /me command."""
	client.send('.action '+line)
	
@client.command(params="[host [port]] ", aliases=["open"])
def connect(params):
	"""Connects to server. host:port format is also allowed. Port is assumed to be 23 if not supplied."""
	
	def parse_port(s):
		if re.match('^[0-9]+$', s) is None:
			return -1
		num = int(s)
		if num <= 0 or num > 65535:
			return -1
		return num

	def connect_usage():
		client.echo("Valid argument formats are:")
		client.echo("/connect")
		client.echo("/connect <host>")
		client.echo("/connect <host> <port>")
		client.echo("/connect <host>:<port>")
		client.echo("Where <port>, if supplied, is greater than 0 and less than or equal to 65535.")
	
	params = params.strip()
	parts = params.split()
	TELNET_PORT = 23
	
	if len(parts) == 0:
		client.connect()
	elif len(parts) == 1:
		arg = parts[0]
		i = arg.find(':')
		if i == -1:
			client.connect(host, TELNET_PORT)
		else:
			host = arg[:i]
			port_str = arg[i+1:]
			port = parse_port(port_str)
			if port == -1:
				client.echo("Invalid port: %s" % port_str)
				connect_usage()
			else:
				client.connect(host, port)
	elif len(parts) == 2:
		host = parts[0]
		port = parse_port(parts[1])
		if port == -1:
			client.echo("Invalid port: %s" % parts[1])
			connect_usage()
		else:
			client.connect(host, port)
	else:
		client.echo("Too many arguments supplied.")
		connect_usage()
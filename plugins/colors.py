from pyclient.api import *

client = ClientAPI()

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

#!/usr/bin/env python
import Config
import os

# Put config in ~/.pyclient.
# We use os.path.expanduser() instead of directly accessing the $HOME environment
# variable because it also works for us neatly on Windows.
#CONFIG_PATH = os.path.join(os.environ['HOME'], '.pyclient')
CONFIG_PATH = os.path.expanduser('~/.pyclient/pyclient.cfg')

def load_config():
	"""Load configuration information."""
	Config.currentConfig.reset()
	if os.path.exists(CONFIG_PATH):
		print 'Loading config from', CONFIG_PATH
		Config.currentConfig.load(CONFIG_PATH)
	else:
		print CONFIG_PATH, "doesn't exist, using default settings"
		
def main():
	"""PyClient main entrypoint."""
	
	# Optionally load Psyco.
	try:
		import psyco
		psyco.full()
		print '* Accelerating with psyco!'
	except:
		print "* Couldn't import psyco, continuing unaccelerated without it."
		print "  If you wish to use psyco to accelerate Python programs, visit"
		print "  the Psyco website: http://psyco.sourceforge.net"

	# TODO: Complain about gtk and twisted and whatnot...

	# I think Twisted does this for us...
	#pygtk.require('2.0')

	# TODO: Is there a 'nicer' way to do this?
	from twisted.internet import gtk2reactor
	gtk2reactor.install()
	from twisted.internet import reactor

	load_config()

	# Run stuff...
	from GTKClient import GTKClient
	client = GTKClient()
	reactor.run()
	
	print 'Saving config to', CONFIG_PATH
	Config.currentConfig.save(CONFIG_PATH)


if __name__ == '__main__':
	main()

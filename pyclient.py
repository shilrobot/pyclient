#!/usr/bin/env python

# Optionally load Psyco before everything else...
try:
	import psyco
	psyco.full()
	print '* Accelerating with psyco!'
except:
	print "* Couldn't import psyco, continuing unaccelerated without it."
	print "  If you wish to use psyco to accelerate Python programs, visit"
	print "  the Psyco website: http://psyco.sourceforge.net"

# Install GTK reactor before we do any Twisted based stuff
from twisted.internet import gtk2reactor
gtk2reactor.install()
	
# Run PyClient
import Client
client = Client.Client()
client.run()
client.shutdown()

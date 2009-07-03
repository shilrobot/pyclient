#!/usr/bin/env python

# Optionally load Psyco before everything else...
try:
	import psyco
	psyco.full()
except:
	pass
	
# Install GTK reactor before we do any Twisted based stuff
from twisted.internet import gtk2reactor
gtk2reactor.install()

# Run PyClient
from pyclient.Client import Client
client = Client(__file__)

from pyclient.GTKClient import GTKClient
#self.ui = GTKClient(self)
		
client.run(GTKClient(client))
client.shutdown()

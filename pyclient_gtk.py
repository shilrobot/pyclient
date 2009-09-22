#!/usr/bin/env python

# Optionally load Psyco before everything else...
try:
	import psyco
	psyco.full()
except:
	pass
	
# Create the core client
from pyclient.Client import Client
client = Client(__file__)

# Create the GTK UI for the client
from pyclient.GTKClient import GTKClient
import gtk

# If we don't do this, pygtk won't let other threads get the GIL
gtk.gdk.threads_init() 

# Set up
client.start(GTKClient(client))

# GTK main loop
gtk.main()

# Tear down
client.shutdown()



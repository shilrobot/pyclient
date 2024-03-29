#!/usr/bin/env python

# Optionally load Psyco before everything else...
try:
	import psyco
	psyco.full()
except:
	pass

# Install GTK reactor before we do any Twisted based stuff
#from twisted.internet import gtk2reactor
#gtk2reactor.install()

import signal
f = open("signals.txt","w")
def standin(x,y):
	f.write("%d %s\n" % (x,y))
	f.flush()
f.write("SIG_IGN=%d\n" % signal.SIG_IGN)
f.write("SIG_DFL=%d\n" % signal.SIG_DFL)

#signal.signal = standin

import curses
from CursesClient import CursesClient	
from twisted.internet import reactor

import Client
client = Client.Client()
	
def main(scrn):
	cc = CursesClient(client,scrn,f)
	reactor.addReader(cc)
	f.write("sighandler for SIGWINCH=%s\n" % signal.getsignal(signal.SIGWINCH))
	f.flush()
	client.run(cc)
	
curses.wrapper(main)
client.shutdown()
 

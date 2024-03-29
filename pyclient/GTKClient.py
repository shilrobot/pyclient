"""The main client window code"""

import gtk,pango,gobject
#from TwistedClient import *
from GTKOutputCtrl import GTKOutputCtrl
import Version
#import Config
from Connection import *
import os
import time

try:
	import glib
	have_glib = True
except:
	have_glib = False

def _idle_add(f):
	# newer versions of pygtk use glib.idle_add instead of gobject.idle_add
	if have_glib and hasattr(glib, 'idle_add'):
		glib.idle_add(f)
	else:
		gobject.idle_add(f)

# TODO: Make a class for the *window itself*

class GTKClient:
	"""Controls the main client window"""
	
	# OH GOD THIS FUNCTION IS TOO LONG
	def __init__(self, client):
		#TwistedClient.__init__(self)
		self._client = client
		self.cfg = client.cfg
		
		# Set up the main window frame
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		# TODO: This doesn't work if we don't run from the base dir!
		self.window.set_icon_from_file(client.getPath('logo-new.png'))
		#self.window.set_border_width(5)
		self.window.connect('delete_event', self.delete_event)
		self.window.connect('destroy', self.destroy)
		self.window.set_title('Tiberian Adventure - PyClient')
		self.window.set_position(gtk.WIN_POS_CENTER)

		# Create the output window
		self.output = GTKOutputCtrl(self.cfg)
		self.output.show()
		
		# Create the scrollbar for the output window
		self.scroll = gtk.ScrolledWindow()
		hpolicy = gtk.POLICY_AUTOMATIC
		if self.cfg.get('output/gtk24wrapping',False):
			hpolicy = gtk.POLICY_NEVER
		self.scroll.set_policy(hpolicy, gtk.POLICY_ALWAYS)
		# TODO: Remove the border between the scrollbar & the control!
		#self.scroll.set_property('scrollbar-spacing', 0)
		self.scroll.add(self.output)
		self.scroll.set_shadow_type(gtk.SHADOW_IN)
		self.scroll.show()

		# Create the input box
		self.input = gtk.TextView()
		self.input.modify_font(pango.FontDescription(self.cfg['input/font']))
		self.input.set_size_request(25,25)
		self.input.connect('key-press-event', self.key_press_event)
		self.input.show()

		self.scroll2 = gtk.ScrolledWindow()
		self.scroll2.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		#self.scroll2.set_size_request(0,-1)
		#self.scroll.set_property('border_width', 0)
		self.scroll2.add(self.input)
		self.scroll2.set_shadow_type(gtk.SHADOW_IN)
		self.scroll2.show()

		panes = gtk.VPaned()
		#panes.add1(self.scroll)
		panes.pack1(self.scroll, resize=True, shrink=False)
		#panes.add2(self.input)
		panes.pack2(self.scroll2, resize=False, shrink=True)
		#if pos != -1:
		#	panes.set_position(pos)
		panes.show()
		self.panes = panes
		#self.window.add(panes)

		# Create the vertical box spacer
		vbox = gtk.VBox()
		#vbox.pack_start(self.scroll)
		#vbox.pack_start(self.input, expand=False)
		vbox.show()
		self.window.add(vbox)

		notebook = gtk.Notebook()
		#hbox = gtk.HBox()
		#hbox.pack_start(gtk.Label("Main"))
		#hbox.show()
		#label = gtk.Label("Main")
		hbox = gtk.HBox()
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_NETWORK, gtk.ICON_SIZE_MENU)
		icon.show()
		label = gtk.Label("Main")
		label.show()
		hbox.pack_start(icon)
		hbox.pack_start(label, padding=2)
		notebook.append_page(panes, hbox)
		notebook.set_show_tabs(True)
		#notebook.set_border_width(5)
		notebook.show()
		panes.set_border_width(4)
		#self.window.add(notebook)

		menubar,tb = self.createActions()
		menubar.show()
		tb.set_property("toolbar-style", gtk.TOOLBAR_ICONS)
		tb.show()

		# Eh, disable menu for now until it's done
		vbox.pack_start(menubar, expand=False)
		vbox.pack_start(tb, expand=False)
		vbox.pack_start(notebook, padding=4)
		#vbox.pack_start(panes) # No notebook background for now
		
		statusBar = gtk.Statusbar()
		vbox.pack_start(statusBar, False, False)
		statusBar.show()
		statusBar.push(0, "Welcome to PyClient")
		self.statusbar = statusBar
		

		# Set up a bunch of stuff
		# TODO: Reorg.
		self.restoreWindowPosition()
		self.window.show()

		# Start out with focus on the input control
		self.input.grab_focus()

		# Register commandx0r
		self._client.addCommand('clear', self.clear, None,
								'Clears the screen.')
		self._client.addCommand(['quit', 'exit'], self.quit, None,
								'Quits the client.')
		#self._client.addCommand('testlogin', self.testLogin, None, 'Tests login dialog')

		self._client = client
		#self._client.ui = self
		self._client.conn.callback = lambda: _idle_add(self._client.conn.update)
		#self._netCallback
		#self._client.events.register('conn.dataReceived', self._onDataReceived)
		#self._client.events.register('client.echo', self._onEcho)
		
		#self.updateUI()
		self._destroying = False
		self.stateChanged(self._client.conn.getState())

		# Display some basic info when we start up
		#self.startupBanner()
		

	def restoreWindowPosition(self):
		"""Restores the old window configuration from the config file."""
		if 'ui/pos' in self.cfg:
			pos = self.cfg['ui/pos']
			self.window.move(*pos[0:2])
		if 'ui/size' in self.cfg:
			size = self.cfg['ui/size']
			self.window.resize(*size[0:2])
		if 'ui/panePos' in self.cfg:
			self.panes.set_position(self.cfg['ui/panePos'])
	
	def saveWindowSettings(self):
		"""Saves the window position to a self.cfg file."""
		# TODO: This doesn't get called when we Ctrl+C pyclient
		# 		from a terminal
		# TODO: Save maximization state
		self.cfg['ui/pos'] = self.window.get_position()
		self.cfg['ui/size'] = self.window.get_size()
		self.cfg['ui/panePos'] = self.panes.get_position()

	def createActions(self):
		ui = '''\
		<ui>
			<menubar name="MenuBar">
				<menu action='Client'>
					<menuitem action='Connect'/>
					<menuitem action='Disconnect'/>
					<separator/>
					<menuitem action='Close'/>
				</menu>
				<menu action='Edit'>
					<!--
					<menuitem action='Cut'/>
					<menuitem action='Copy'/>
					<menuitem action='Paste'/>
					<separator/>
					-->
					<menuitem action='Preferences'/>
				</menu>
				<menu action='View'>
					<menuitem action='Clear'/>
				</menu>
				<menu action='Help'>
					<menuitem action='ShowCommands'/>
					<menuitem action='About'/>
				</menu>
			</menubar>
			<toolbar name="ToolBar">
				<toolitem action='Connect'/>
				<toolitem action='Disconnect'/>
				<toolitem action='Preferences'/>
			</toolbar>
		</ui>
		'''
		actiongroup = gtk.ActionGroup("ClientActions")
		actiongroup.add_actions([("Client", None, "_Client"),
								 	("Connect", gtk.STOCK_CONNECT, "_Connect", None, "Connect to the server"),
								 	("Disconnect", gtk.STOCK_DISCONNECT, "_Disconnect", None, "Disconnect from the server"),
								 	("Close", gtk.STOCK_CLOSE),
								 ("Edit", None, "_Edit"),
								 	("Cut", gtk.STOCK_CUT),
								 	("Copy", gtk.STOCK_COPY),
								 	("Paste", gtk.STOCK_PASTE),
								 	("Preferences", gtk.STOCK_PREFERENCES),
								 ("View", None, "_View"),
								 	("Clear", gtk.STOCK_CLEAR, "_Clear Screen"),
								 ("Help", None, "_Help"),
								 	("ShowCommands", gtk.STOCK_HELP, "_Show Command List"),
								 	("About", gtk.STOCK_ABOUT)
								])
		uimanager = gtk.UIManager()
		uimanager.insert_action_group(actiongroup, 0)
		uimanager.add_ui_from_string(ui)
		accelgroup = uimanager.get_accel_group()
		self.window.add_accel_group(accelgroup)
		self.uimanager = uimanager
		self.actions = actiongroup
		self.connectActions()
		return uimanager.get_widget("/MenuBar"), uimanager.get_widget('/ToolBar')
		
	def linkAction(self, name, cb):
		self.actions.get_action(name).connect('activate', cb)
		
	def connectActions(self):
		self.linkAction('Connect', lambda e: self._client.execute("/connect"))
		self.linkAction('Disconnect', lambda e: self._client.execute("/close"))
		self.linkAction('Clear', self.clear)
		self.linkAction('Close', self.quit)
		self.linkAction('ShowCommands', lambda e: self._client.execute("/help"))

	def clear(self, args=''):
		self.output.clear()
		
	def testLogin(self, args=''):
		import LoginDialog
		dlg = LoginDialog.LoginDialog(self.window)
		dlg.run()
		dlg.destroy()
		
	def key_press_event(self, widget, event, data=None):
		if event.string == '\r' and not (event.state & gtk.gdk.SHIFT_MASK):
			if isinstance(self.input, gtk.Entry):
				#self.interpret(self.input.get_text())
				self._client.execute(self.input.get_text())
				self.input.set_text('')
			elif isinstance(self.input, gtk.TextView):
				buffer = self.input.get_buffer()
				start, end = buffer.get_bounds()
				text = buffer.get_text(start,end)
				#self.interpret(text)
				self._client.execute(text)
				buffer.set_text('')
			return True

	def delete_event(self, widget, event, data=None):
		"""Called when the user requests a window close via the WM, e.g.
		by clicking the window close button in the titlebar."""
		self.saveWindowSettings()
		# Return False to tell GTK to destroy the window
		return False 

	def destroy(self, widget=None, data=None):
		"""Called during GTK window destruction. At this point it's
		already too destroyed to check the window size and so on,
		so we have to do that in the delete event."""
		self._destroying = True
		gtk.main_quit()
		
	def onReceiveText(self, chunks):
		self.output.write(chunks)

	def quit(self, args=''):
		self.destroy()

	#def __del__(self):
	#	reactor.stop()
		
	def stateChanged(self, newstate):
		#print '*** stateChanged'
		if self._destroying:
			return
		connect = self.actions.get_action("Connect")
		connect.set_sensitive(newstate == STATE_DISCONNECTED)
		disconnect = self.actions.get_action("Disconnect")
		disconnect.set_sensitive(newstate != STATE_DISCONNECTED)
		self.statusbar.pop(0)
		statename = {STATE_DISCONNECTED: 'Disconnected',
							 STATE_CONNECTING: 'Connecting',
							 STATE_CONNECTED: 'Connected'}[newstate]
		self.statusbar.push(0, "PyClient %s / %s" % (Version.VERSION_NAME, statename))


	#def _onEcho(self, line):
	#	self.onReceiveText(line+"\r\n")
		
	#def _onDataReceived(self, data):
	#	self.onReceiveText(text)

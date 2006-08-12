import gtk

class LoginDialog(gtk.Dialog):
	"""Dialog for doing login."""
	
	def __init__(self, parent=None, username='', password='', rememberPassword=False):# autoLogin=False):
		gtk.Dialog.__init__(self, parent=parent,
									buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
											gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
		
		# Save settings
		self.username = username
		self.password = password
		self.rememberPassword = rememberPassword
				
		tooltips = gtk.Tooltips()
				
		table = gtk.Table()
		table.set_col_spacing(0, 4)
		self.vbox.add(table)
		
		usernameLabel = gtk.Label("Username:")
		usernameLabel.set_alignment(1, 0.5)
		table.attach(usernameLabel, 0, 1, 0, 1)
				
		self.usernameEntry = gtk.Entry()
		self.usernameEntry.set_text(self.username)
		self.usernameEntry.set_activates_default(True)
		table.attach(self.usernameEntry, 1, 2, 0, 1)
		
		passwordLabel = gtk.Label("Password:")
		passwordLabel.set_alignment(1, 0.5)
		table.attach(passwordLabel, 0, 1, 1, 2)
		
		self.passwordEntry = gtk.Entry()
		self.passwordEntry.set_property("visibility", False)
		self.passwordEntry.set_text(self.password)
		self.passwordEntry.set_activates_default(True)
		table.attach(self.passwordEntry, 1, 2, 1, 2)
		
		self.rememberPasswordCheck = gtk.CheckButton("Remember Password")
		self.rememberPasswordCheck.set_active(rememberPassword)
		tooltips.set_tip(self.rememberPasswordCheck, "Check to save your password so you don't have to re-enter it")
		table.attach(self.rememberPasswordCheck, 0, 2, 2,3)
		
		#self.autoLoginCheck = gtk.CheckButton("Enable Auto-Login")
		#self.autoLoginCheck.set_active(autoLogin)
		#tooltips.set_tip(self.autoLoginCheck, "Check to automatically log in the next time you connect")
		#self.autoLoginCheck.set_active(rememberPassword)
		#table.attach(self.autoLoginCheck, 0, 2, 3,4)
		
		self.set_default_response(gtk.RESPONSE_ACCEPT)
		self.set_title('Log In')
		self.show_all()
		
		if username != '':
			self.passwordEntry.grab_focus()
	
	#def destroy(self, evt=None):
	#	self.response(gtk.RESPONSE_REJECT)
		
if __name__ == '__main__':
	dialog = LoginDialog(None, 'shilbert', 'foobar', False)
	result = dialog.run()
	print dialog.username, dialog.password, dialog.rememberPassword, result

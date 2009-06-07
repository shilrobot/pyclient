"""Miscellaneous plugins."""
__author__ = 'Scott Hilbert <me@shilbert.com>'
__version__ = '1.0' # TODO: Does this *have* to be a revision number?

# TODO: Guess pyclient has to become a package
from pyclient import client

# Auto-generate parsing rules from the parameter list!

def cmd_me(text):
	"""Alternative to .action for people used to IRC."""
	client.send(".action "+text)
	
def cmd_colors():
	"""Displays TA colorcodes for reference."""
	client.echo("...")

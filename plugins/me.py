from pyclient.api import *

@command
def me(line):
	"""Emulation of IRC /me command."""
	send('.action '+line)

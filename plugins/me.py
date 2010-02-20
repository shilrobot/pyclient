from pyclient.api import *

client = ClientAPI()

@client.command
def me(line):
	"""Emulation of IRC /me command."""
	client.send('.action '+line)

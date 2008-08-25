import re
CMD_REGEX = re.compile(r'^/([a-zA-Z0-9_-]+)([ \t](.*))?$')

while 1:
	s = raw_input('Cmdline: ')
	m = CMD_REGEX.match(s)
	print m
	if m is not None:
		print m.groups()
# Tokenizer.py - handles all the telnet/TA2 parsing

from Constants import *

# We use an empty string as the end-of-buffer character.
EOB = ''

# TODO: Make token interfaces more uniform (getters, etc.)

class Token:
	"""
	Abstract base class for all tokens.
	"""
	def __init__(self, text=''):
		assert isinstance(text, str), "text must be a string"
		self.text = text
		
	def __ne__(self, other): return not self.__eq__(other)

	def __eq__(self, other):
		if not isinstance(other, self.__class__): return False
		return self.text == other.text

	def __repr__(self):
		return "%s(text=%s)" % (self.__class__.__name__, self.text)

class WaitToken(Token):
	"""
	Token that means there's not enough data to produce
	an actual token just yet, call back later.
	"""
	#def __eq__(self, other):
	#	return isinstance(other, WaitToken)

class NewlineToken(Token):
	"""
	Represents a CRLF linebreak.
	"""
	pass

class TextToken(Token):
	"""
	A token representing an ubroken chunk of text.
	Will only contain ASCII characters.
	"""
	pass
	#def __init__(self, text):
	#	self.text = text

	#def __eq__(self, other):
	#	if not isinstance(other, TextToken): return False
	#	return self.text == other.text

	#def __repr__(self):
	#	return "TextToken(text=%s)" % repr(self.text)
	
class AnsiCodeToken(Token):
	"""
	A token representing a single ANSI color code escape,
	such as "\x1b[31m".
	"""
	def __init__(self, text, number):
		Token.__init__(self, text)
		self.number = number

	def __eq__(self, other):
		if not isinstance(other, AnsiCodeToken): return False
		return self.number == other.number

	def __repr__(self):
		return "AnsiCodeToken(text=%s, number=%s)" % \
				(self.text, self.number)

class TA2Token(Token):
	"""
	Token that represents a TA2 escape code, possibly with
	a color code and unicode value.
	"""
	def __init__(self, text, flags, color=0, unicode=0):
		Token.__init__(self, text)
		assert isinstance(flags, int), "Flags must be integer"
		assert isinstance(color, int), "Color must be integer"
		assert isinstance(unicode, int), "Druink Unicode must be integer"
		self._flags = flags
		self._color = color
		self._unicode = unicode

	def __eq__(self, other):
		if not isinstance(other, TA2Token): return False
		return self._flags == other._flags and \
				self._color == other._color and \
				self._unicode == other._unicode

	def __repr__(self):
		return 'TA2Token(text=%s, flags=%d,color=0x%x,unicode=0x%x)' % \
				(self.text, self._flags, self._color, self._unicode)

	def getFlags(self): return self._flags
	def getColor(self): return self._color
	def getUnicode(self): return self._unicode

class XmlToken(Token):
	"""
	Token that represents a TA2 XML block.
	"""
	def __init__(self, text, xml=''):
		Token.__init__(self, text)
		self.xml = xml

	def __eq__(self, other):
		if not isinstance(other, XmlToken): return False
		return self.xml == other.xml

	def __repr__(self):
		return 'XmlToken(text=%s, xml=%s)' % \
				(self.text, self.xml)

# Parsing states for ProtocolParser
# This isn't a strict telnet parser btw :P
ST_INITIAL = 0
ST_TEXT = 1
ST_EXPECT_NEWLINE = 9

# Normal ANSI color stuff
ST_EXPECT_LBRACK = 2
ST_EXPECT_NUMBER = 3
ST_EXPECT_NUMBER_OR_M = 4
ST_EXPECT_M = 5

# TA2/EV/DruinkMUD extended stuff
ST_EXPECT_TA2_COLOR = 6
ST_EXPECT_TA2_UNICODE = 7
ST_EXPECT_TA2_XML = 8

def ishexdigit(x):
	"""
	Possibly the laziest way of checking if a string is a hex character
	ever created.
	"""
	return x in '0123456789abcdefABCDEF'

# TODO: Have a text state that makes the abort-with-text-token and
#       producing-text-token-before-entering-new-state behavior
# 		simpler
# TODO: More flexible ANSI code parsing (; separators)
class Tokenizer:
	"""
	Parses the input stream into text and escape-command tokens.
	It understands basic ANSI telnet color codes (i.e. ESC[#m) as well as
	TA2 coloring codes.
	"""
	def __init__(self):
		self.state 				= ST_INITIAL # Parser state
		self.queue				= '' # Data in our 'receive buffer' to process
		self._setupLookahead()
		self.text 				= '' # Buffer for text of current token.
									 # This accumulates text for ALL tokens!
		self.ta2flags			= 0  # Current TA2 flags, if we're parsing
									 # a TA2 escape
		self.color 				= '' # Current color accum buffer, as text
		self.unicode 			= '' # Current Unicode accum buffer, as text
		self.xml 				= '' # Current XML accum buffer, as text

	def queueData(self, data):
		"""
		Adds data to the to-be-parsed queue.
		"""
		self.queue += data
		self._setupLookahead()

	def _setupLookahead(self):
		"""
		Fixes up lookahead info.
		"""
		# Since EOB is equivalent to '', this is a nice
		# quick way of doing it...
		self.la = self.queue[:1]
	
	def _next(self):
		"""
		Eats a character from the queue.
		"""
		assert len(self.queue) >= 1, "Can't move past end of buffer!"
		# We do this here automatically now
		self.text += self.la
		self.queue = self.queue[1:]
		self._setupLookahead()

	def _brokenToken(self):
		"""
		Called when a token appears to be malformed.
		It assumes the first character of the token was actually text,
		and continues parsing from the second character.
		"""
		tmp = self.text
		self.queue = tmp[1:] + self.queue
		self.text = tmp[0]
		self._setupLookahead()
		self.state = ST_TEXT

	# HERE THERE BE DRAGONS
	# This can always use commenting, cleanup, extra consistency, etc.
	def getNextToken(self):
		while self.la != EOB:
			# Default state. Expecting either an ANSI escape code,
			# EV escape code, or some normal characters.
			if self.state == ST_INITIAL:
				# Start clean.
				self.text = ''

				# ANSI escape code
				if self.la == '\x1b':
					self._next()
					self.state = ST_EXPECT_LBRACK
				# EV escape code
				# TODO: Handle text correctly
				elif ord(self.la) & ATT_ID:
					self.ta2flags = ord(self.la)
					self.color = ''
					self.unicode = ''
					self._next()
					if self.ta2flags & ATT_SET and self.ta2flags & ATT_COLOR:
						self.state = ST_EXPECT_TA2_COLOR
					elif self.ta2flags & ATT_SET and \
						 self.ta2flags & ATT_UNICODE:
						self.state = ST_EXPECT_TA2_UNICODE
					else:
						self.state = ST_INITIAL
						return TA2Token(self.text, self.ta2flags)
				# EV XML embed
				# TODO: Handle text correctly
				elif self.la == '\x19':
					self.state = ST_EXPECT_TA2_XML
					self.xml = ''
					self._next()
				elif self.la == '\r':
					self.state = ST_EXPECT_NEWLINE
					self._next()
				else:
					self._next()
					self.state = ST_TEXT
			# We're in the middle of a text token
			elif self.state == ST_TEXT:
				if self.la != '\x1b' and not (ord(self.la) & ATT_ID) and \
					self.la != '\x19' and self.la != '\r':
					self._next()
				else:
					self.state = ST_INITIAL
					return TextToken(self.text)
			elif self.state == ST_EXPECT_NEWLINE:
				if self.la == '\n':
					self._next()
					self.state = ST_INITIAL
					return NewlineToken(self.text)
				else:
					self._brokenToken()
			# Expecting the [ part of an ANSI escape code
			elif self.state == ST_EXPECT_LBRACK:
				if self.la == '[':
					self._next()
					self.state = ST_EXPECT_NUMBER
				else:
					self._brokenToken()		
			# Expecting first number of ANSI escape code
			elif self.state == ST_EXPECT_NUMBER:
				if self.la.isdigit():
					self.digits = self.la
					self._next()
					self.state = ST_EXPECT_NUMBER_OR_M
				else:
					self._brokenToken()
			# Expecting second number of ANSI escape code, or 'm'
			elif self.state == ST_EXPECT_NUMBER_OR_M:
				if self.la.isdigit():
					self.digits += self.la
					self._next()
					self.state = ST_EXPECT_M
				elif self.la == 'm':
					self.text += self.la
					self._next()
					#self._applyAnsiCode(digits)
					#self.text = ''
					self.state = ST_INITIAL
					return AnsiCodeToken(self.text, int(self.digits))
				else:
					self._brokenToken()
			# Expecting 'm'
			elif self.state == ST_EXPECT_M:
				if self.la == 'm':
					self._next()
					self.state = ST_INITIAL
					return AnsiCodeToken(self.text, int(self.digits))
				else:
					self._brokenToken()
			# Expecting EV color after EV escape
			elif self.state == ST_EXPECT_TA2_COLOR:
				if ishexdigit(self.la):
					self.color += self.la
					self._next()
					if len(self.color) == 6:
						if self.ta2flags & ATT_SET and \
							self.ta2flags & ATT_UNICODE:
							self.state = ST_EXPECT_TA2_UNICODE
						else:
							# TODO: Convert to int
							self.state = ST_INITIAL
							return TA2Token(self.text, self.ta2flags, \
											int(self.color,16))
				else:
					self._brokenToken()
			# Expecting EV unicode after EV escape (and maybe after color)
			elif self.state == ST_EXPECT_TA2_UNICODE:
				if ishexdigit(self.la):
					self.unicode += self.la
					self._next()
					if len(self.unicode) == 6:
						self.state = ST_INITIAL
						if self.ta2flags & ATT_SET and \
							self.ta2flags & ATT_COLOR:
							return TA2Token(self.text, self.ta2flags, \
									int(self.color,16), int(self.unicode,16))
						else:
							return TA2Token(self.text, self.ta2flags, \
									unicode=int(self.unicode,16))
				else:
					self._brokenToken()
			# Expecting XML or something something
			elif self.state == ST_EXPECT_TA2_XML:
				if self.la == '\x19':
					self._next()
					self.state = ST_INITIAL
					return XmlToken(self.text, self.xml)
				else:
					self.xml += self.la
					self._next()
			# Something else (which shouldn't happen)
			else:	
				assert 0, "Invalid parser state, omg wtf!!1~ :("
		
		# Send any text we may have found...	
		if self.state == ST_TEXT:
			self.state = ST_INITIAL
			return TextToken(self.text)
		else:
			return WaitToken() 


__all__ = ['Token',
			'WaitToken',
			'NewlineToken',
			'TextToken',
			'AnsiCodeToken',
			'TA2Token',
			'XmlToken',
			'Tokenizer']
	

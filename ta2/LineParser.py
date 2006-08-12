from Constants import *
from Tokenizer import *
from copy import copy
import re


class AnsiColor(object):
	"""ANSI/telnet color code. The 'code' attribute is an integer from 0 to 7.
	If you get a chunk with this type of color, most likely you will
	have to use a lookup table to convert it to a proper RGB color.
	"""	
	
	def __init__(self, code):
		assert isinstance(code, int) and code >= 0 and code <= 7, \
				"code must be an integer from 0 to 7: %d" % code
		self.code = code
		
	def __eq__(self, other):
		return self.code == other.code
		
	def __ne__(self, other):
		return not self.__eq__(other)
		
		
class TA2Color(object):
	"""TA2 'truecolor' color code. The 'code' attribute is an HTML-style
	color string, e.g. '#FFFFFF'.
	"""

	# Used for verifying color codes in the constructor.
	# Matches HTML colors.
	_regex = re.compile("#[0-9a-fA-F]{6}")

	def __init__(self, code):
		assert self._regex.match(code), \
				"code must be an HTML color, e.g. '#FFFFFF'; got %s" % code
		self.code = code
		
	def __eq__(self, other):
		return self.code == other.code
		
	def __ne__(self, other):
		return not self.__eq__(other)
		

class TextStyle(object):
	"""A set of style information for a TextChunk.
	This is enough to totally style any chunk we receive from TA.
	"""
	
	def __init__(self, color=None, bold=False, \
				italic=False, underline=False, strikethrough=False):
		"""Constructor.
		Note that color can be None (i.e., default color), an AnsiColor,
		or an HtmlColor.
		"""
		self.color = color
		self.bold = bold
		self.italic = italic
		self.underline = underline
		self.strikethrough = strikethrough

	def __eq__(self, other):
		if not isinstance(other, TextStyle): return False
		return self.color == other.color and \
				self.bold == other.bold and \
				self.italic == other.italic and \
				self.underline == other.underline and \
				self.strikethrough == other.strikethrough

	def __ne__(self, other):
		return not self.__eq__(other)

	def clone(self, **kwargs):
		"""
		Makes a copy of this style object, with optional
		modifications. Names of the attributes here are the same
		as in the constructor.
		"""
		defargs = {'color':copy(self.color),
					'bold':self.bold,
					'italic':self.italic,
					'underline':self.underline,
					'strikethrough':self.strikethrough}
		defargs.update(kwargs)
		return TextStyle(**defargs)


# TODO: This doesn't *do* anything -- should we get rid of it?
class Chunk(object):
	"""
	Base class for all line parts
	"""
	pass


class TextChunk(Chunk):
	"""
	Represents a chunk of styled text.
	"""

	def __init__(self, text='', style=None):
		assert isinstance(text, str), "Text must be str instance"
		if style == None:
			self.style = TextStyle()
		else:
			assert isinstance(style, TextStyle), \
					"style must be TextStyle instance"
			self.style = style
		self.text = text

	def __eq__(self, other):
		if not isinstance(other, TextChunk): return False
		return self.text == other.text and self.style == other.style

	def __ne__(self, other):
		return not self.__eq__(other)


class XmlChunk(Chunk):
	"""
	An XML block.
	"""

	def __init__(self, xml=''):
		assert isinstance(xml, str), "xml must be str instance"
		self.xml = xml

	def __eq__(self, other):
		if not isinstance(other, XmlChunk): return False
		return self.xml == other.xml

	def __ne__(self, other):
		return not self.__eq__(other)
		

class LineParser(object):
	"""
	Assembles tokens into lines composed of TextChunks.
	This takes care of giving each TextChunk a correct TextStyle
	based on the flags present in the coloring tokens.
	"""

	def __init__(self):
		self._tokenizer = Tokenizer()
		self._incompleteLine = []
		self._completeLines = []
		self._reset()

	def _reset(self):
		"""
		Resets text style info.
		"""
		self._style = TextStyle()


	def getLine(self):
		"""
		Gets a line from the tokenizer.
		This will be None if there isn't one ready, otherwise it
		will return a list of Chunks. The newline character will
		not be included in the last chunk.
		"""
		if len(self._completeLines) > 0:
			return self._completeLines.pop(0)
		else:
			return None
		
	def queueData(self, data):
		"""
		Queues a chunk of data and parses it for line retrieval later.
		"""
		assert isinstance(data, str), "data must be string"
		self._tokenizer.queueData(data)
		# Tokenize now...
		while 1:
			tok = self._tokenizer.getNextToken()
			if isinstance(tok, WaitToken):
				break
			elif isinstance(tok, TextToken):
				self._incompleteLine.append(TextChunk(tok.text, self._style))
			elif isinstance(tok, AnsiCodeToken):
				if tok.number == 0:
					self._reset()
				elif tok.number == 1:
					self._style = self._style.clone(bold=True)
				elif tok.number >= 30 and tok.number <= 37:
					colorNum = tok.number - 30
					self._style = self._style.clone(color=AnsiColor(colorNum))
			elif isinstance(tok, TA2Token):
				flags = tok.getFlags()
				setting = (flags & ATT_SET)!=0
				if flags & ATT_BOLD:
					self._style = self._style.clone(bold=setting)	
				if flags & ATT_ITALIC:
					self._style = self._style.clone(italic=setting)
				if flags & ATT_UNDERLINE:
					self._style = self._style.clone(underline=setting)
				if flags & ATT_STRIKETHROUGH:
					self._style = self._style.clone(strikethrough=setting)
				if flags & ATT_COLOR:
					if setting:
						self._style = \
							self._style.clone(color=TA2Color('#%06x'%tok.getColor()))
					else:
						self._style = \
							self._style.clone(color=None)
				# TODO: Actually test this
				# TODO: This will be really slow if someone were to post a line
				#		in Japanese, for example -- every single character
				#		would result in a discrete text chunk!
				if flags & ATT_UNICODE:
					text = chr(tok.getUnicode())
					self._incompleteLine.append(TextChunk(text, self._style))
			elif isinstance(tok, NewlineToken):
				self._completeLines.append(self._incompleteLine)
				self._incompleteLine = []
			elif isinstance(tok, XmlToken):
				self._incompleteLine.append(XmlChunk(tok.xml))


__all__ = ['AnsiColor',
			'TA2Color',
			'TextStyle',
			'Chunk',
			'TextChunk',
			'XmlChunk',
			'LineParser',
			'AnsiColor']

import gtk, pango, gobject
from ta2 import *
import re

# TODO: Clean some of this up to the extent possible...
class GTKOutputCtrl(gtk.TextView):
	"""
	Control that displays the colorized/formatted output from TA.
	"""

	def __init__(self, cfg):
		gtk.TextView.__init__(self, buffer=None)
		self.cfg = cfg
		self.set_wrap_mode(gtk.WRAP_WORD_CHAR)
		
		states = [gtk.STATE_NORMAL, gtk.STATE_ACTIVE, gtk.STATE_PRELIGHT, gtk.STATE_INSENSITIVE]
		for state in states:
			for func in [self.modify_base, self.modify_bg]:
				func(state, gtk.gdk.color_parse(self.cfg['output/bg/default']))
								 
		self.modify_text(gtk.STATE_NORMAL, \
				gtk.gdk.color_parse(self.cfg['output/fg/default']))
		self.modify_font(pango.FontDescription(self.cfg['output/font']))
		self.set_editable(False)
	
		# Tags and such
		self._buffer = self.get_buffer()
		self._colorTags = {}
		self._forceBG = self._buffer.create_tag(background=self.cfg['output/bg/default'])
		self._boldTag = self._buffer.create_tag(weight=pango.WEIGHT_BOLD)
		self._italicTag = self._buffer.create_tag(style=pango.STYLE_ITALIC)
		self._underlineTag = \
			self._buffer.create_tag(underline=pango.UNDERLINE_SINGLE)
		self._strikethroughTag = self._buffer.create_tag(strikethrough=True)
		self._urlTag = \
			self._buffer.create_tag(underline=pango.UNDERLINE_SINGLE, \
									foreground=self.cfg['output/urls'], weight=pango.WEIGHT_BOLD)

		self._barCursor = gtk.gdk.Cursor(gtk.gdk.XTERM)
		self._arrowCursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
		self._handCursor = gtk.gdk.Cursor(gtk.gdk.HAND2)

		self.connect('motion-notify-event', self._motionNotify)
		#self._urlTag.connect('event', self._textEvent)
		#self._urlTag.set_data('url', 'http://www.google.com')
		self.set_events(gtk.gdk.ALL_EVENTS_MASK)

		# TODO: More elaborate...?
		# TODO: More comprehensive TLD's
		# TODO: Technically your browser shouldn't handle mailto and FTP, necessarily...
		# TODO: We can do this *once* instead of every time we make a class,
		#		although it's probably not too heavyweight
		self._urlRegex = re.compile(r"(mailto:[^\s']+|(http|ftp)://[^\s']+|www\.[^\s']+|[^\s']+\.(com|org|net|us|gov|biz|uk|ca)((/|\?)[^\s']*)?)", re.IGNORECASE)

	def _motionNotify(self, widget, event):
		if event.is_hint:
			self.get_pointer()
		x,y = self.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET, int(event.x), int(event.y))
		iter = self.get_iter_at_location(x,y)
		isUrl = False
		url = ''
		for tag in iter.get_tags():
			if tag.get_data('url') != None:
				isUrl = True
				url = tag.get_data('url')
		if isUrl:
			event.window.set_cursor(self._handCursor)
		else:
			event.window.set_cursor(self._barCursor)
		return False
		
	def _openBrowser(self, url):
		import webbrowser
		urllower = url.lower()
		# If the url doesn't have an attached protocol, then
		# prepend http://
		if not re.match('^(http|ftp|mailto):', url):
			url = 'http://'+url
		webbrowser.open(url)		

	# TODO: Protect against link double-click
	# TODO: Rename this better
	def _textEvent(self, tag, widget, event, iter=None, userParam=None):
		if event.type != gtk.gdk.BUTTON_RELEASE:
			return
		# Only care about left button
		if event.button != 1:
			return
		# Ignore it if they were just trying to make a selection
		if self._buffer.get_selection_bounds():
			return
		try:
			url = tag.get_data('url')
			self._openBrowser(url)
		except:
			import traceback as tb
			tb.print_exc()

	def _colorObjectToHTML(self, color):
		"""Converts from a color object specified in a TextChunk to an HTML color code"""
		if color is None:
			return self.cfg['output/fg/default']
		elif isinstance(color, AnsiColor):
			return self.cfg['output/fg/colors'][color.code]
		else: # TA2Color
			assert isinstance(color, TA2Color)
			return color.code
					
	def _getColorTag(self, color):
		"""Creates a new text tag for a color if one doesn't exist yet."""
		color = color.lower()
		tag = self._colorTags.get(color)
		if tag == None:
			tag = self._buffer.create_tag(foreground=color)
			self._colorTags[color] = tag
		return tag
	
	def _insertChunk(self, chunk):
		"""
		I don't know what else I could say that's not already
		in the function name...
		"""
		style = chunk.style
		text = chunk.text
		tags = [self._forceBG, self._getColorTag(self._colorObjectToHTML(style.color))]
		if style.bold:
			tags.append(self._boldTag)
		if style.italic:
			tags.append(self._italicTag)
		if style.underline:
			tags.append(self._underlineTag)
		if style.strikethrough:
			tags.append(self._strikethroughTag)
		#print repr(text)
		self._buffer.insert_with_tags(self._buffer.get_end_iter(),text, *tags)
		end = self._buffer.get_end_iter()
		
		# TODO: Cleaner way of doing this (that will withstand tags in the middle, etc.)
		# TODO: Anything else we should add?
		for match in self._urlRegex.finditer(text):
			startpos = match.start()
			endpos = match.end()
			# Ignore periods on the end
			if match.group()[-1] == '.':
				endpos -= 1
			urlStart = end.copy()
			urlEnd = end.copy()
			urlStart.forward_chars(-len(text)+startpos)
			urlEnd.forward_chars(-len(text)+endpos)
			self._urlify(text[startpos:endpos], urlStart, urlEnd)
	
	def _urlify(self, url, startIter, endIter):
		# TODO: Actually extract URL here
		tag = self._buffer.create_tag()
		tag.set_data('url', url)
		tag.connect('event', self._textEvent)
		self._buffer.remove_all_tags(startIter, endIter)
		self._buffer.apply_tag(self._urlTag, startIter, endIter)
		self._buffer.apply_tag(tag, startIter, endIter)
	
	def _insertNewline(self):
		self._buffer.insert(self._buffer.get_end_iter(), "\n")

	def write(self, chunks):
		"""Parses and writes text to the output control, and
		scrolls it into view
		"""
		for c in chunks:
			self._insertChunk(c)
		self._insertNewline()
		mark = self._buffer.create_mark(None, self._buffer.get_end_iter())
		self.scroll_to_mark(mark, 0)

	def clear(self):
		"""Clears the buffer."""
		self._buffer.set_text('')

		
__all__ = ['GTKOutputCtrl']
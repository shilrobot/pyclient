from ta2 import *
import cgi
import os
import datetime
import time

LOG_HEADER = """\
<html>
<head>
<title>%s</title>
<style type="text/css">
body {
	background-color: black;
	color: white;
	font-family: Courier New;
	font-size: 10pt;
}
</style>
</head>
<body>
"""

class Log:
	def __init__(self, client):
		self._client = client
		self._parser = LineParser()
		self._currCol = '#FFFFFF'
		
	def _doStyles(self, style):
		s = ''
		if style.bold:
			s += '<b>'
		if style.underline:
			s += '<u>'
		if style.italic:
			s += '<i>'
		if style.strikethrough:
			s += '<s>'
		if style.color is not None:
			if isinstance(style.color, AnsiColor):
				hexcode = self._client.cfg.getStr('output/fg/%d' % style.color.code)
			else:
				hexcode = style.color.code
			s += '<span style="color:%s">'%hexcode
		return s
			
	def _undoStyles(self, style):
		s = ''
		if style.bold:
			s += '</b>'
		if style.underline:
			s += '</u>'
		if style.italic:
			s += '</i>'
		if style.strikethrough:
			s += '</s>'
		if style.color is not None:
			s += '</span>'
		return s
			
		
	def _writeChunks(self, chunks):
		logDir = self._client.getPath("logs")
		if not os.path.exists(logDir):
			try:
				os.mkdir(logDir)
			except:
				return
		logFile = self._client.getPath(time.strftime("logs/%Y-%m-%d.html"))
		new = not os.path.exists(logFile)
		try:
			fp = open(logFile, "a")
		except:
			return
		if new:
			title = time.strftime("pyclient log for %A, %B %d %Y")
			fp.write(LOG_HEADER % title)
		#s = '<span class="time">%s</span> ' % time.strftime("%X")
		s=''
		nbsp = True
		for chunk in chunks:
			s += self._doStyles(chunk.style)
			#escaped = cgi.escape(chunk.text)
			#escaped = escaped.replace("  ", "&nbsp; ")
			for c in cgi.escape(chunk.text):
				if c == ' ':
					if nbsp:
						s += '&nbsp;'
					else:
						s += ' '
					nbsp = not nbsp
				else:
					s += c
			#s += escaped
			s += self._undoStyles(chunk.style)
		s += '<br>\n'
		fp.write(s)
		fp.close()		
		
	def write(self, data):
		self._parser.queueData(data)
		while 1:
			line = self._parser.getLine()
			if line == None:
				break
			else:
				textChunks = []
				for chunk in line:
					if isinstance(chunk, XmlChunk):
						pass
					else:
						textChunks.append(chunk)
				if len(textChunks) > 0:
					self._writeChunks(textChunks)
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
	font-family: Mono, Courier New, Courier;
	font-size: 10pt;
}
</style>
</head>
<body>
"""

class Log:

	def __init__(self, client):
		self._client = client
		self._currCol = '#FFFFFF'
		self._logPath = None
		self._logFile = None
		self._acquireLog()
		
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
				hexcode = self._client.cfg['output/fg/colors'][style.color.code]
			else:
				hexcode = style.color.code
			s += '<font color="%s">'%hexcode
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
			s += '</font>'
		return s
		
	def _acquireLog(self):
		desiredPath = self._client.getPath(time.strftime("logs/%Y-%m-%d.html"))
		if self._logFile is None or self._logPath != desiredPath:
		
			if self._logFile is not None:
				self._logFile.close()
				self._logPath = None
				self._logFile = None
				
			newLog = not os.path.isfile(desiredPath)
				
			logDir = self._client.getPath("logs")
			if not os.path.exists(logDir):
				try:
					os.mkdir(logDir)
				except:
					return False
					
			try:
				f = open(desiredPath, "a")
			except:
				return False
				
			self._logFile = f
			self._logPath = desiredPath
				
			if newLog:
				title = time.strftime("pyclient log for %A, %B %d %Y")
				self._logFile.write(LOG_HEADER % title)
		return True		
		
	def _writeChunks(self, chunks):
		s=''
		nbsp = True
		for chunk in chunks:
			s += self._doStyles(chunk.style)
			#s += cgi.escape(chunk.text)
			for c in cgi.escape(chunk.text):
				if c == ' ':
					if nbsp:
						s += '&nbsp;'
					else:
						s += ' '
					nbsp = not nbsp
				else:
					s += c
					nbsp = False
			s += self._undoStyles(chunk.style)
		s += '<br>\n'
		self._logFile.write(s)
		self._logFile.flush()
		
	def write(self, chunks):
		if self._acquireLog():
			self._writeChunks(chunks)

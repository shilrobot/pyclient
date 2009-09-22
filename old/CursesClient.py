
import curses
import curses.wrapper
import signal

C_BLACK 	= 0
C_RED		= 1
C_GREEN 	= 2
C_YELLOW	= 3
C_BLUE		= 4
C_MAGENTA	= 5
C_CYAN		= 6
C_WHITE 	= 7

class InputBox:
	def __init__(self, win):
		self.x = 0
		self.y = 0
		self.w = 1
		self.h = 1
		self.win = win
		self.text = ""
		self.pos = 0
		self.scroll = 0
		self.onLineEntered = None
		
	def move(self, n):
		if n > len(self.text):
			n = len(self.text)
		if n < 0:
			n = 0
		if n == self.pos:
			return
		self.pos = n
			
	def adjustScroll(self):
		if self.pos - self.scroll < 0:
			self.scroll = self.pos
		elif self.pos > self.scroll+self.w-1:
			self.scroll = self.pos-self.w+1 	
		
	def moverel(self, n):
		self.move(self.pos+n)
		
	def onCharEntered(self, c):
		if c >= ord(' ') and c <= ord('~'):
			self.text = self.text[:self.pos] + chr(c) + self.text[self.pos:]
			self.moverel(1)
		elif c == curses.KEY_LEFT:
			self.moverel(-1)
		elif c == curses.KEY_RIGHT:
			self.moverel(+1)
		elif c == curses.KEY_HOME:
			self.move(0)
		elif c == curses.KEY_END:
			self.move(len(self.text))
		elif c == curses.KEY_BACKSPACE:
			if self.pos > 0:
				self.text = self.text[0:self.pos-1] + self.text[self.pos:]
				self.moverel(-1)
		elif c == curses.KEY_DC:
			if self.pos < len(self.text):
				self.text = self.text[0:self.pos] + self.text[self.pos+1:]
		elif c == ord('\n') or c == curses.KEY_ENTER:
			if self.onLineEntered is not None:
				self.onLineEntered(self.text)
			self.text = ''
			self.move(0)
				
	def paint(self):
		self.adjustScroll() 
		try:
			self.win.addstr(self.y, self.x, self.text[self.scroll:][:self.w-1])
		except:
			pass
		self.win.move(self.y, self.x+self.pos-self.scroll)

class CursesClient:
	def __init__(self, client, scrn,f):
		self.f =f
		self.client = client
		self.scrn = scrn
		self.scrn.nodelay(1)
		self.output = ""
		self.inputBox = InputBox(scrn)
		self.inputBox.onLineEntered = self.client.execute	
		self.client.addCommand(["quit","exit"], self.quit, '', 'Exits the client')	
		#signal.signal(signal.SIGWINCH, self.handleit)
		self.n = 0
		
	def handleit(self,*args):
		self.f.write("SIGWINCH\n")
		self.f.flush()
		self.paint()
		
	def quit(self, params):
		from twisted.internet import reactor
		reactor.stop()
		
	def fileno(self):
		""" We want to select on FD 0 """
		return 0
	
	def paint(self):
		self.scrn.erase()
		self.scrn.addstr(0,0,self.output)
		self.scrn.addstr(0,0,"|/-\\"[self.n])
		#self.scrn.addstr(24,0,self.input)
		h,w = self.scrn.getmaxyx()
		self.inputBox.x = 0
		self.inputBox.y = h-1
		self.inputBox.w = w
		self.inputBox.h = 1
		self.inputBox.paint()
		self.n += 1
		if self.n == 4:
			self.n = 0
		self.scrn.refresh()
		
	def doRead(self):
		"""called when input is ready"""
		#import pyclient_curses
		#import signal
		#self.f.write("sighandler for SIGWINCH=%s\n" % signal.getsignal(signal.SIGWINCH))
		#self.f.flush()
		
		#signal.signal(signal.SIGWINCH, self.handleit)
		#while True:
		c = self.scrn.getch()
		#signal.signal(signal.SIGWINCH, self.handleit)
		#if c == -1:
		#	break
		self.inputBox.onCharEntered(c)
		self.paint()
	
	def logPrefix(self):
		return 'CursesClient'		
		
	def onReceiveText(self, data):	
		s = ''
		for c in data:
			if ord(c) == ord('\n') or (ord(c) >= ord(' ') and ord(c) <= ord('~')):
				s += c
		self.output += s
		self.paint()
		
	def stateChanged(self, state):
		pass
		
	
		
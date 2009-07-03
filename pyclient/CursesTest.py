

import curses
import curses.wrapper
import curses.textpad
import random
import signal

C_BLACK = 0
C_RED = 1
C_GREEN = 2
C_YELLOW = 3
C_BLUE = 4
C_MAGENTA = 5
C_CYAN = 6
C_WHITE = 7

class InputBox:
	def __init__(self, win):
		self.text = ""
		self.pos = 0
		self.win = win
		self.scroll = 0
		
	def move(self, n):
		if n > len(self.text):
			n = len(self.text)
		if n < 0:
			n = 0
		if n == self.pos:
			return
		self.pos = n
		#self.adjustScroll()
			
	def adjustScroll(self):
		self.w = self.win.getmaxyx()[1]
		if self.pos - self.scroll < 0:
			self.scroll = self.pos
		elif self.pos > self.scroll+self.w-1:
			self.scroll = self.pos-self.w+1		
		
	def moverel(self, n):
		self.move(self.pos+n)
		
	def char(self, c):
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
		elif c == ord('\n'):
			self.text = ''
			self.move(0)
				
	def draw_str_scrolled(self,y, x, n, scroll, text):
		#print y,x,scroll,text
		# TODO: Remove the -1, it's sort of stupid here... It has to do w/ the cursor
		# TODO: This f's up the cursor state, relative to what curses thinks it has, methinks >:|
		try:
			self.win.addstr(y, x, text[scroll:][:self.w-1])
		except:
			self.win.move(0,0)
			pass
		
				
	def draw(self):
		self.adjustScroll()
		self.win.erase()	
		#self.win.addstr(0, 0, "[")
		#self.win.addstr(0, 1, self.text)		
		self.draw_str_scrolled(0, 0, self.w, self.scroll, self.text)
		#self.win.addstr(0, 1+self.w, "]")
		#self.win.addstr(1,0,"pos=%d scroll=%d strlen=%d"%(self.pos, self.scroll, len(self.text)))
		self.win.move(0, self.pos-self.scroll)

log = open("signals2.txt","w")

import time		

def f(stdscr):
	h,w = stdscr.getmaxyx()
	stdscr.nodelay(1)

	curses.init_pair(C_RED, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(C_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(C_YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(C_BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
	curses.init_pair(C_MAGENTA, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	curses.init_pair(C_CYAN, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(C_WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)
	
	stdscr.bkgd(' ', curses.color_pair(0))
	#stdscr.border(0, 5, 0, 5)
	#for n in range(0,9):
		#rgb = curses.color_content(n|curses.A_NORMAL)
		#stdscr.addstr(n,0,"%s"%curses.color_pair(n))
	#stdscr.addstr(0,0,"TIBERIA",curses.color_pair(C_GREEN))
	
	#lol = curses.newwin(10,10,0,0)
	#tp = curses.textpad.Textbox(lol)
	
	inputWin = curses.newwin(1,w,h-1,0)
	ib = InputBox(inputWin)
	ib.draw()
	#stdscr.move(h-1,0)
	#stdscr.addstr(h-1,0,("0123456789"*20)[:w-1])
	#stdscr.inch(h-1,w-2,"X")
	#stdscr.scrollok(1)
	#stdscr.border(0, w-1, 0, h-1, 0, 0, 0, 0)
	while 1:
		log.write("sighandler for SIGWINCH=%s\n"% signal.getsignal(signal.SIGWINCH))
		c = stdscr.getch()
		if c == -1:
			time.sleep(0.1)
			continue
		ib.char(c)
		ib.draw()
		h,w = stdscr.getmaxyx()
		inputWin.mvwin(h-1,0)
		inputWin.refresh()
	
log.write("sighandler for SIGWINCH=%s\n"% signal.getsignal(signal.SIGWINCH))
curses.wrapper(f)


from pyclient.api import *
import random
import math
import time

TOKEN_LENGTH = 6
TOKEN_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

ST_IDLE="ST_IDLE"
ST_WAIT="ST_WAIT"

def _genToken():
	s = ''.join(random.choice(TOKEN_CHARS) for x in range(TOKEN_LENGTH))
	return s
	
class Pinger:
	def __init__(self):
		self.reset()
		
	def reset(self):
		self._state = ST_IDLE
		self._startTime = None
		self._token = None
		self._maxPings = 0
		self._pingTimes = []
		
	def sendPing(self, maxPings):
		if not isConnected():
			echo("Not connected!")
			return
		elif self._state == ST_WAIT:
			echo("Ping already in progress")
			return
		assert maxPings > 0
		self._maxPings = maxPings
		self._sendOnePing()
		
	def _sendOnePing(self):
		self._startTime = time.time()
		self._state = ST_WAIT
		self._token = _genToken()
		send(".ping " + self._token)		

	def receivePing(self, line):
		if self._state != ST_WAIT:
			return False
		if len(line) < TOKEN_LENGTH + len("Pong! "):
			return False
		rxToken = line[-TOKEN_LENGTH:]
		if rxToken == self._token:
			pingTime = time.time() - self._startTime
			print 't=%.3f'%pingTime
			#echo('Ping: %d ms' % round(pingTime*1000))
			self._pingTimes.append(pingTime)
			if len(self._pingTimes) >= self._maxPings:
				self._report()
				self.reset()
			else:
				self._sendOnePing()
			return True
		return False
		
	def _report(self):
		assert len(self._pingTimes) > 0
		minPing = min(self._pingTimes)
		maxPing = max(self._pingTimes)
		avgPing = sum(self._pingTimes) / len(self._pingTimes)
		sse = 0
		for t in self._pingTimes:
			sse += (t - avgPing)**2
		if len(self._pingTimes) == 1:
			stdev = 0
		else:
			var = sse / (len(self._pingTimes) - 1)
			if var > 1e-6:
				stdev = math.sqrt(var)
			else:
				stdev = 0
		echo(('Ping '+EV_RED+'min'+EV_NORMAL+'/'+EV_YELLOW+'avg'+EV_NORMAL+'/'+EV_GREEN+'max'+EV_NORMAL+'/'+EV_CYAN+'stdev'+EV_NORMAL+': '+
				     EV_RED+'%d'+EV_NORMAL+'/'+EV_YELLOW+'%d'+EV_NORMAL+'/'+EV_GREEN+'%d'+EV_NORMAL+'/'+EV_CYAN+'%d'+EV_NORMAL+' ms')
				% (round(minPing*1000),
					round(avgPing*1000),
					round(maxPing*1000),
					round(stdev*1000)))
			
pinger = Pinger()
	
# TODO: This should only be done once...
def _combineChunks(chunks):
	s = ''
	for c in chunks:
		s += c.text
	return s
	
@hook('lineReceived')
def lineReceived(chunks):
	text = _combineChunks(chunks)
	if text.startswith('Pong!'):
		return pinger.receivePing(text)
	else:
		return False
	
@hook('connected')
def connected():
	pinger.reset()
	
@hook('disconnected')
def disconnected():
	pinger.reset()
	
@command
def ping(args):
	pinger.sendPing(10)


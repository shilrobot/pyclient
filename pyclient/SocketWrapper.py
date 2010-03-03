import socket
import Queue
import select
import threading
import time

ST_INIT				= "ST_INIT"
ST_CONNECTING		= "ST_CONNECTING"
ST_CONNECTED		= "ST_CONNECTED"
ST_DISCONNECTING	= "ST_DISCONNECTING"
ST_DISCONNECTED		= "ST_DISCONNECTED"

EVT_CONNECTED				= "EVT_CONNECTED"
EVT_CONNECT_FAILED			= "EVT_CONNECT_FAILED"
EVT_RECV					= "EVT_RECV"
EVT_READ_THREAD_DONE		= "EVT_READ_THREAD_DONE"
EVT_READ_THREAD_EXCEPTION	= "EVT_READ_THREAD_EXCEPTION"

class SocketWrapper:
	def __init__(self):
		self._state = ST_INIT
		self._sock = socket.socket()
		# infinite queue length
		self._evtQ = Queue.Queue(0)
		self._mainThread = threading.currentThread()
		self._readThread = None
		self.callback = None
		
	def _get_state(self):
		self._checkMainThread()
		return self._state
		
	state = property(_get_state)
						
	def _evt(self, evt, arg=None):
		#print time.time(), evt, arg
		self._evtQ.put((evt,arg))
		if self.callback is not None:
			self.callback()
		
	def connect(self, host, port):
		self._checkMainThread()
		assert self._state == ST_INIT
		self._state = ST_CONNECTING
		self._readThread = threading.Thread(target=self._readThreadFunc, args=(host,port))
		self._readThread.start()
	
	def close(self):
		self._checkMainThread()
		assert self._state != ST_INIT
		if self._state == ST_CONNECTING or self._state == ST_CONNECTED:
			try:
				#print 'closing socket'
				# This will cause the thread to eventually finish
				self._sock.shutdown(2)
			except socket.error:
				pass
			#wasConnected = self._state == ST_CONNECTED
			self._state = ST_DISCONNECTING
			#if wasConnected:
			#	self.disconnected()
			#else:
			#	print 'canceling in-progress connection'
			#	self.connectionFailed()
				
	def send(self, data):
		# if we ever noticeably block sending on a telnet server we are doing something wrong
		self._checkMainThread()
		assert self._state in [ST_CONNECTED, ST_DISCONNECTING]
		if self._state == ST_DISCONNECTING:
			return
		while len(data) > 0:
			try:
				bytesSent = self._sock.send(data)
			except:
				self.close()
				return
			data = data[bytesSent:]
		
	def update(self):
		self._checkMainThread()
		while 1:
			try:
				(evt,data) = self._evtQ.get(False)
			except:
				break
			if evt == EVT_CONNECTED:
				if self._state == ST_CONNECTING:
					self._state = ST_CONNECTED
					self.connected()
			elif evt == EVT_CONNECT_FAILED:
				assert self._state == ST_CONNECTING
				self._state = ST_DISCONNECTED
				self.connectionFailed()
			elif evt == EVT_RECV:
				# TODO: What is proper state here?
				# Ugh ignore data past disconnects...
				if self._state == ST_CONNECTED:
					self.dataReceived(data)
			elif evt in [EVT_READ_THREAD_DONE,
						 EVT_READ_THREAD_EXCEPTION]:
				if self._state == ST_CONNECTED or self._state == ST_DISCONNECTING:
					self._state = ST_DISCONNECTED
					self._sock.close()
					self.disconnected()
		
	def _readThreadFunc(self, host, port):
		# This thread should automatically close if the socket is closed
		#print time.time(), 'Read thread created'
		try:
			self._sock.connect((host,port))
		except socket.error:
			self._evt(EVT_CONNECT_FAILED)
			return
		#print time.time(), 'Connected'
		self._evt(EVT_CONNECTED)
		while 1:
			try:
				#print 'Recving...'
				data = self._sock.recv(4096)
				#print 'Done Recving'
			except socket.error:
				self._evt(EVT_READ_THREAD_EXCEPTION)
				return
			if data == '':
				break
			else:
				self._evt(EVT_RECV, data)
		#print 'Read thread ran out of data'
		#print time.time(), 'Read thread ran out of data'
		self._evt(EVT_READ_THREAD_DONE)
		
	def _checkMainThread(self):
		assert threading.currentThread() is self._mainThread
					
	def dataReceived(self, data):
		#print 'dataReceived(%s)' % repr(data)
		pass
		
	def connected(self):
		#print 'connected()'
		pass
		
	def connectionFailed(self):
		#print 'connectionFailed()'
		pass
		
	def disconnected(self):
		#print 'disconnected()'
		pass
			
__all__ = ['Socket', 'ST_INIT', 'ST_CONNECTING', 'ST_CONNECTED', 'ST_DISCONNECTING', 'ST_DISCONNECTED']

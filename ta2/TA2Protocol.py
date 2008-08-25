from twisted.internet.protocol import Protocol
from LineParser import *
from xml.etree.ElementTree import fromstring

# TODO: Reconcile TA2Protocol's keeping a separate LineParser for every connection
#       and the way PyClient used to work -- keeping one LineParser that everything
#		just piled into

# TODO: Maybe have a protocol that handles all the XML for us?

class TA2Protocol(Protocol):
	"""Tiberian Adventure version 2 protocol.
	
	When a connection is made, the line 'ta2\r\n' is immediately sent to the
	server to initiate a TA2 login."""
	
	def __init__(self):
		"""Constructor"""
		self._lineParser = LineParser()
		
	def connectionMade(self):
		# Called by Twisted when the connection is made
		self.sendLine('ta2')

	def dataReceived(self, data):
		# This method is called by Twisted when we receive data
		
		# Queue in the line parser
		self._lineParser.queueData(data)
		
		# While there are lines left...
		# TODO: Is there a simpler way to do this bit, with
		#		generators or iterators or something?
		while 1:
			line = self._parser.getLine()
			
			# LineParser returns None if there are no more
			# lines ready
			if line is not None:
				# If we got an XmlChunk, it is always on a line by itself;
				# we send it to xmlReceived
				if len(line) == 1 and isinstance(line[0], XmlChunk):
					self.rawXmlReceived(chunk.xml)
				# Otherwise, it should be all TextChunk's, and we
				# route it to lineReceived
				else:
					for chunk in line:
						assert isinstance(chunk, TextChunk), "Expected only text chunks in this line, but got %s" % repr(chunk)
					self.lineReceived(line)
		
	def lineReceived(self, chunks):
		"""Called when a line of normal text is received."""
		# Derived classes can implement a handler for this
		pass
		
	def sendLine(self, line):
		"""Sends a single line to the server. CRLF is automatically inserted."""
		self.transport.write(line + '\r\n')		
		
	def rawXmlReceived(self, xml):
		"""Called when an XML string is received. At this stage it is unparsed."""
		#print 'Got XML:', xml
		try:
			element = fromstring(xml)
		except:
			self.malformedXmlReceived(xml)
		else:
			self.xmlReceived(element)
			
	def malformedXmlReceived(self, xml):
		"""Called when an XML string fails parsing"""
		# Derived classes can implement a handler for this
		pass
		
	def xmlReceived(self, element):
		"""Called when valid XML is received"""
		# Derived classes can implement a handler for this
		# TODO: Do we want to put all this handling in one class or have an TA2XMLProtocol or something?
		handler = 'xml_'+(element.tag.replace('-','_'))
		func = getattr(self, handler, None)
		if func != None:
			func(element)
		else:
			xml_unknownTag(element)
			
	def xml_unknownTag(self, element):
		print 'No handler',handler		
					

__all__ = ['TA2Protocol']

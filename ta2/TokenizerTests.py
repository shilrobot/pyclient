import unittest
from Constants import *
from Tokenizer import *

# TODO: Clean this stuff up more.. and test the tests! Be more precise!
# TODO: Test tokens?

class TestTokenizer(unittest.TestCase):

	# Damn this is getting hairy... hairy like Chewbacca :(
	#
	# The issue with collapsing text is that it causes some of the checks that
	# are supposed to make sure the parser acts as expected (i.e. stops at the appropriate
	# points to spit out text) to stop working :/
	#
	# This needs fixing...
	def _testParsing(self, st, *L):
		'''Tests that parsing a particular string all at once will return the given
		sequence of tokens. The Wait token at the end is implicit.'''
		# TODO: Test parsing it character-by-character too!
		#print 'Testing '+repr(st)
		L = self._collapseText(list(L)) + [WaitToken()]
		p = Tokenizer()
		p.queueData(st)
		resultToks = []
		while 1:
			tok = p.getNextToken()
			resultToks.append(tok)
			if isinstance(tok, WaitToken):
				break
		resultToks = self._collapseText(resultToks)
		self.assertEqual(len(L), len(resultToks), "Error parsing '%s': Expected token list %s, got %s" % \
							(repr(st), repr(L), repr(resultToks)))
		for tok,result in zip(L,resultToks):
			self.assertEqual(tok, result, \
								"Error parsing '%s': Expected %s but got %s" % \
							 	(repr(st), repr(L), repr(resultToks)))
		self.assertEqual(p.getNextToken(), WaitToken(),
							'When waiting, repeated calls to getNextToken() should '+\
							'continue to return WaitForMoreDataTokens')

	def _collapseText(self, toks):
		text = ''
		result = []
		for t in toks:
			if isinstance(t, TextToken):
				text += t.text
			else:
				if text != '':
					result.append(TextToken(text))
					text = ''
				result.append(t)
		if text != '':
			result.append(TextToken(text))
		return result

	def _testPrefixAndSuffix(self, pref, suf, st, *args):
		args = list(args) 
		if pref != '':
			args.insert(0, TextToken(pref))
		if suf != '':
			args.append(TextToken(suf))
		args = self._collapseText(args)
		self._testParsing(pref+st+suf, *args)
		pass

	def _testBeforeAndAfter(self, st, *args):
		self._testPrefixAndSuffix('', '', st, *args)	# TODO: Sexier/cleaner way
		self._testPrefixAndSuffix('a', '', st, *args)
		self._testPrefixAndSuffix('', 'b', st, *args)
		self._testPrefixAndSuffix('abc', 'def', st, *args)
		self._testPrefixAndSuffix('oh emm gee', 'ell oh ell', st, *args)
		doubleargs = args[:] + args[:]
		self._testPrefixAndSuffix('','', st+st, *doubleargs)
		# TODO: Do some stuff

	def testGetNextToken(self):
		# TODO: Parsing numbers > 2 digits; parsing ;-separated numbers; etc.
		self._testParsing('')
		self._testParsing('a', TextToken('a'))
		self._testParsing('a\x1b', TextToken('a'))
		self._testParsing('a\x1b[', TextToken('a'))
		self._testParsing('a\x1b[3', TextToken('a'))
		self._testParsing('a\x1b[31', TextToken('a'))
		self._testParsing('a\x1b[31m', TextToken('a'), AnsiCodeToken('\x1b[31m]', 31))
		self._testParsing('a\x1b[31mb', TextToken('a'), AnsiCodeToken('\x1b[31m', 31), TextToken('b'))
		self._testParsing('abcdefg', TextToken('abcdefg'))
		self._testParsing('a\x1b[31a', TextToken('a'), TextToken('\x1b[31a'))
		self._testParsing('\x1b[5m', AnsiCodeToken('\x1b[5m', 5))
		self._testBeforeAndAfter('')
		self._testBeforeAndAfter('\x1b[31m', AnsiCodeToken('\x1b[31m', 31))
		self._testBeforeAndAfter('\x19\x19', XmlToken('\x19\x19', ''))
		self._testBeforeAndAfter('\x19<sup/>\x19', XmlToken('\x19<sup/>\x19', '<sup/>'))

		# Test TA2/Druink stuff
		code = ATT_ID|ATT_SET|ATT_BOLD
		self._testBeforeAndAfter(chr(code), TA2Token(chr(code), code))
		code = ATT_ID|ATT_SET|ATT_COLOR
		self._testBeforeAndAfter(chr(code)+"abcdef", TA2Token(chr(code)+"abcdef", code, color=0xabcdef))
		# Case of unset color
		code = ATT_ID|ATT_COLOR
		self._testBeforeAndAfter(chr(code)+"abcdef", TA2Token(chr(code), code), TextToken("abcdef"))
		code = ATT_ID|ATT_SET|ATT_UNICODE
		self._testBeforeAndAfter(chr(code)+"abcdef", TA2Token(chr(code)+"abcdef", code, unicode=0xabcdef))
		code = ATT_ID|ATT_UNICODE
		self._testBeforeAndAfter(chr(code)+"abcdef", TA2Token(chr(code), code), TextToken("abcdef"))
		code = ATT_ID|ATT_SET|ATT_COLOR|ATT_UNICODE
		self._testBeforeAndAfter(chr(code)+"abcdef"+"123456", \
								TA2Token(chr(code)+"abcdef123456", code, 0xabcdef, 0x123456))
		code = ATT_ID|ATT_COLOR|ATT_UNICODE
		self._testBeforeAndAfter(chr(code)+"abcdef"+"123456", TA2Token(chr(code), code), TextToken("abcdef123456"))

		# Test partial TA2 codes
		code = ATT_ID|ATT_SET|ATT_COLOR
		self._testBeforeAndAfter(chr(code)+"abcq", TextToken(chr(code)+"abcq"))
		code = ATT_ID|ATT_SET|ATT_UNICODE
		self._testBeforeAndAfter(chr(code)+"abcq", TextToken(chr(code)+"abcq"))
		code = ATT_ID|ATT_SET|ATT_COLOR|ATT_UNICODE
		self._testBeforeAndAfter(chr(code)+"abcdef123Q", TextToken(chr(code)+"abcdef123Q"))
		

if __name__ == '__main__':
	unittest.main()

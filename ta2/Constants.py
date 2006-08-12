
# ANSI colorcodes
ANSI_RED	= '\x1b[31m'
ANSI_GREEN	= '\x1b[32m'
ANSI_YELLOW = '\x1b[33m'
ANSI_BLUE	= '\x1b[34m'
ANSI_PINK	= '\x1b[35m'
ANSI_CYAN	= '\x1b[36m'
ANSI_WHITE	= '\x1b[37m'
ANSI_BOLD	= '\x1b[1m'
ANSI_NORMAL	= '\x1b[0m'

# TA2/EV escape code flags (rev 2)
# See the PDF and .H file at http://tiberia.homeip.net/ev/ for more info
ATT_ID 				= 0x80 # Always set for escape codes
ATT_SET 			= 0x40
ATT_BOLD			= 0x20
ATT_ITALIC 			= 0x10
ATT_UNDERLINE 		= 0x08
ATT_COLOR 			= 0x04
ATT_STRIKETHROUGH 	= 0x02
ATT_UNICODE 		= 0x01 # Only used by DruinkMUD so far, AFAIK

# New EV tags
CODE_B		= '<-b>'
CODE_I		= '<-i>'
CODE_U		= '<-u>'
CODE_S		= '<-s>'
CODE_NB		= '<-/b>'
CODE_NI		= '<-/i>' # AAARGH
CODE_NU		= '<-/u>'
CODE_NS		= '<-/s>'

# EV classic tag equivalents
EV_SETCOLOR	= chr(ATT_ID|ATT_SET|ATT_COLOR)
EV_RED		= EV_SETCOLOR+"FF0000"
EV_GREEN	= EV_SETCOLOR+"00FF00"
EV_YELLOW	= EV_SETCOLOR+"FFFF00"
EV_BLUE		= EV_SETCOLOR+"0000FF"
EV_PINK		= EV_SETCOLOR+"FF00FF"
EV_CYAN		= EV_SETCOLOR+"00FFFF"
EV_WHITE	= EV_SETCOLOR+"FFFFFF"
EV_NORMAL	= chr(ATT_ID|ATT_BOLD|ATT_ITALIC| \
					ATT_UNDERLINE|ATT_COLOR|ATT_STRIKETHROUGH|ATT_UNICODE)

# Equivalent code for EV tags
EV_B		= chr(ATT_ID|ATT_SET|ATT_BOLD)
EV_I		= chr(ATT_ID|ATT_SET|ATT_ITALIC)
EV_U		= chr(ATT_ID|ATT_SET|ATT_UNDERLINE)
EV_S		= chr(ATT_ID|ATT_SET|ATT_STRIKETHROUGH)
EV_NB		= chr(ATT_ID|ATT_BOLD)
EV_NI		= chr(ATT_ID|ATT_ITALIC)
EV_NU		= chr(ATT_ID|ATT_UNDERLINE)
EV_NS		= chr(ATT_ID|ATT_STRIKETHROUGH)

# Some aliases
EV_BOLD = EV_B
EV_RESET = EV_NORMAL



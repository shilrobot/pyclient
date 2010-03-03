"""
Contains version information.
"""

class Version:
	def __init__(self, number, name, epithet):
		self.number = number
		self.name = name
		self.epithet = epithet

# Kept here for easy reference. Newer ones go later in the list.
VERSION_HISTORY = [
	Version(6, "0.06-dev", "Untitled"),
]

# Numerical form of the version.
# A new version should always have a greater number than an old version.
VERSION_NUMBER = VERSION_HISTORY[-1].number

# Textual form of the version, for display.
VERSION_NAME = VERSION_HISTORY[-1].name

# (not so) clever release name
VERSION_EPITHET = VERSION_HISTORY[-1].epithet

# The full name of this PyClient version as a string (sort of like uname -a)
FULLNAME = "PyClient "+VERSION_NAME+" \""+VERSION_EPITHET+"\""

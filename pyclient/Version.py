"""
Contains version information.
"""

# Kept here for easy reference. Newer ones go later in the list.
VERSION_HISTORY = [
	(6, "0.06-dev", "Untitled"),
]

# Numerical form of the version.
VERSION_NUMBER = VERSION_HISTORY[-1][0]

# Textual form of the version.
VERSION_NAME = VERSION_HISTORY[-1][1]

# Release name
VERSION_EPITHET = VERSION_HISTORY[-1][2]

# The full name of this PyClient version
FULLNAME = "PyClient "+VERSION_NAME+" \""+VERSION_EPITHET+"\""

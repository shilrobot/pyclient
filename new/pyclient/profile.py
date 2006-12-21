
from pyclient.core import Component
import os

class Profile(Component):
	"""Component that handles managing the PyClient profile directory."""

	def initComponent(self):
		self.path = os.path.expanduser('~/.pyclient2')
		
	def setPath(self, path):
		self.path = path
		
	def getPath(self, subpath=None):
		if subpath is None:
			return self.path
		else:
			return os.path.join(self.path, subpath)

	def _wantDir(self, subpath=None):
		fullpath = self.getPath(subpath)
		if not os.path.exists(fullpath):
			try:
				os.mkdir(fullpath)
				print 'Created directory: '+fullpath
			except:
				print 'Cannot create directory: '+fullpath
				return False
		return True
		
	def createProfileSkeleton(self):
		self._wantDir()
		self._wantDir('logs')
		self._wantDir('plugins')

__all__ = ['Profile']
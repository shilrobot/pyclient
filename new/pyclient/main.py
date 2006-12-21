from pyclient.core import Component
from pyclient.profile import Profile
from pyclient.config import Config

class Foo(Component):
	implements = ['IConfigListener']
		
	def onConfigChanged(self, *args):
		#print args
		pass

def main():
	Profile().createProfileSkeleton()
	Config().loadConfig()

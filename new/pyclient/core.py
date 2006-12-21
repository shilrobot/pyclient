"""Component architecture implementation."""

import sys


__all__ = ['Interface', 'Component', 'ExtensionPoint']



class Interface(object):
	"""Marker base class for all component interfaces."""
	
	
#def implements(*args):
#	"""Used inside a class body to mark that it implements one or more interface names."""
#	localDict = sys._getframe(1).f_locals
#	localDict.setdefault('implements', []).extend(args)
	
		
class ComponentMetaclass(type):
	"""Metaclass for Component subclasses."""

	# Dictionary mapping Component subclasses -> instances of those subclasses
	_instances = {}
	
	# Dictionary mapping interfaces -> lists of component subclasses that implement them
	_interfaceImpls = {}

	def __new__(meta, name, bases, dict):
		"""Constructs a new class with some magic for singletonness.
		
		@param meta: This will be ComponentMetaclass.
		@param name: Name of component subclass.
		@param bases: Bases tuple of component subclass.
		@param dict: Content dict of component subclass.
		"""
		new_class = super(ComponentMetaclass, meta).__new__(meta, name, bases, dict)
		
		if 'implements' in dict:
			for iface in dict['implements']:
				ComponentMetaclass._interfaceImpls.setdefault(iface, []).append(new_class)
		#print 'cls.__bases__ =',bases
		# TODO: Because it's easy to shadow base classes' implements list,
		# 		maybe check EVERY base to be sure?
		for base in bases:
			if hasattr(base, 'implements'):
				for iface in base.implements:
					ComponentMetaclass._interfaceImpls.setdefault(iface, []).append(new_class)	
		
		# TODO: Shit... This doesn't work if __init__ is in the BASE
		# Replace __init__ with a do-nothing, and save the old
		# one (if applicable) so that we can call it explicitly in our
		# __new__ override for the new class
		if '__init__' in dict:
			oldinit = dict['__init__']
			new_class.__oldinit__ = oldinit
			del new_class.__init__
		else:
			new_class.__oldinit__ = lambda self: None
		# Replace __new__ with a function that will return an existing
		# instance if there is one; otherwise, it will create a new instance
		# directly and explicitly call __init__
		def fake_new(cls):
			if cls in ComponentMetaclass._instances:
				return ComponentMetaclass._instances[cls]
			else:
				inst = super(Component, cls).__new__(cls)
				ComponentMetaclass._instances[cls] = inst
				inst.__oldinit__()		
				inst.doInitComponent()
				return inst
		new_class.__new__ = staticmethod(fake_new)
		
		return new_class
	
	
class ExtensionPoint(property):
	"""Property type that evaluates to a list of all Component instances implementing
	a certain interface."""
	
	def __init__(self, interface):
		self._interface = interface
		
	def __get__(self, inst, owner):
		return [comp() for comp in ComponentMetaclass._interfaceImpls.get(self._interface, [])]
		
		
class Component(object):
	"""Singleton component object."""
	
	__metaclass__ = ComponentMetaclass
	
	def __init__(self):
		passprintf
		
	def doInitComponent(self):
		#print 'Loading component: %s' % repr(self)
		self.initComponent()	
	
	def initComponent(self):
		pass
		
			
if __name__ == '__main__':
	print 'Constructing MyObj class...'
	class MyObj(Component):
		implements = ['A']
		x = 5
		
		def __init__(self):
			print 'MyObj.__init__()'
			print self.x
			
	class MyObjDerived(MyObj):
		implements = ['B']
		X = ExtensionPoint('A')
	
	class MyObj2(Component):
		pass			
			
	print 'Constructing test objects...'
	print MyObj(), MyObjDerived()
	print MyObj().__class__
	print MyObj()
	print MyObj2()
	
	print ComponentMetaclass._interfaceImpls
	print MyObjDerived().X
	
	class A(object):
		pass
	class B(A):
		pass
	class C(B):
		pass
	print C.__class__

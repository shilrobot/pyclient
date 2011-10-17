"""Configuration system for PyClient."""

import json	
import shutil
	
class Config(dict):
	
	def load(self, filename):
		"""
		Loads from the given filename in JSON format, returning a boolean indicating success.
		Note: Contents of config file are ***merged*** with the defaults!
		"""
		try:
			with open(filename, "rb") as f:
				self.update(json.load(f))
			return True
		except Exception, e:
			print 'Config.load: %s: %s' % (filename, e)
			return False
				
	def save(self, filename):
		"""Saves to the given filename in JSON format, returning a boolean indicating success"""
		tmp_filename = filename+".tmp"
		try:
			with open(tmp_filename, "wb") as f:
				json.dump(self, f, indent=2)
			shutil.move(tmp_filename, filename)
			return True
		except Exception, e:
			print 'Config.save: %s: %s' % (filename, e)
			return False

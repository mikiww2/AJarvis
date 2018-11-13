#!/usr/bin/env python3

import logging, sys

class Logger:
	def __init__(self):
#create and setup handler 
		self._handler=logging.StreamHandler(sys.stdout)
		
		if __debug__:
			self._handler.setLevel(logging.DEBUG)
		else:
			self._handler.setLevel(logging.WARN)

		self._handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

	def set_logger(self, logger):
		if __debug__:
			logger.setLevel(logging.DEBUG)
		else:
			logger.setLevel(logging.WARN)

		logger.addHandler(self._handler)

		return logger
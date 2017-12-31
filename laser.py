# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO

class Laser (object):
	"""
	Classe Laser -> permet juste de contrôler le transistor qui ouvre/ferme le circuit du laser
	"""

	def __init__(self, pin):
		self.pin = pin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT)

	def on(self):
		GPIO.output(self.pin, 1)

	def off(self):
		GPIO.output(self.pin, 0)

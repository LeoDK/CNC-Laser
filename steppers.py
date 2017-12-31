# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO
import time
from math import sqrt


################################################################################################
#############################                                        ###########################
#############################     Classe StepperMotor (bas niveau)   ###########################
#############################                                        ###########################
################################################################################################

class StepperMotor (object):

	#Sequence pour a1, b2, a2, b1:
	#Plein pas, couple maximal
	#PHASE_SEQ=[[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]]
	#Résolution doublée : demi pas
	PHASE_SEQ = ((1,0,0,0),(1,1,0,0),(0,1,0,0),(0,1,1,0),(0,0,1,0),(0,0,1,1),(0,0,0,1),(1,0,0,1))

	def __init__(self, a1, a2, b1, b2):
		""" a1 et a2 forment la bobine a, b1 et b2 la bobine b """
		GPIO.setmode(GPIO.BCM)

		self.a1 = a1
		self.a2 = a2
		self.b1 = b1
		self.b2 = b2

		GPIO.setup(self.a1, GPIO.OUT)
		GPIO.setup(self.b1, GPIO.OUT)
		GPIO.setup(self.a2, GPIO.OUT)
		GPIO.setup(self.b2, GPIO.OUT)

		self.phase = 0

		#L'ordre dans lequel on doit activer les bobines
		self.coil_seq = (self.a1, self.b2, self.a2, self.b1)

	def spin(self, steps, speed=5):
		""" Tourne l'axe du moteur de [steps] pas. [speed] en pas/s """
		if steps == 0 : return None

		#On sépare le signe de la valeur algébrique
		direction = ( lambda x : 1 if x>=0 else -1 )(steps)
		steps = abs(steps)
		#v = d/t <=> t = d/v
		delay = 1.0/speed

		for _ in range(steps):
			#Nouvelle phase
			self.phase = (self.phase+direction) % len(StepperMotor.PHASE_SEQ)

			#On alimente dans le bon sens la bobine qui en a besoin
			for i,coil in zip( range(len(self.coil_seq)), self.coil_seq ):
				GPIO.output(coil, StepperMotor.PHASE_SEQ[self.phase][i])

			time.sleep(delay)

	def release(self):
		""" Relâche le moteur """
		GPIO.output(self.a1, 0)
		GPIO.output(self.a2, 0)
		GPIO.output(self.b1, 0)
		GPIO.output(self.b2, 0)

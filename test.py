# -*- coding:utf-8 -*-

"""
Voir si le rPi est bien configuré
"""

from system2D import *
from steppers import StepperMotor
from time import sleep

def basicTest():
	speed = 20
	x = Axis(2, 3, 4, 14, 37, 0.11, speed)
	y = Axis(15, 18, 17, 27, 41, 0.082, speed)

	machine = Machine(x, y, None)
	machine.release()

	machine.setRelativeMode()
	machine.linearMovement(20, 30)

	machine.setAbsoluteMode()
	sleep(1)
	machine.circularInterpolation(28, 30, 4, 4, -1)

	machine.release()

def testY():
	y = Axis(15, 18, 17, 27, 39, 0.082, 3)
	y.setRelativeMode()
	y.move(20)

def testX():
	x = Axis(2, 3, 4, 14, 39, 0.11, 3)
	x.setRelativeMode()
	x.move(20)

def calbrateMotor():
	stepper = StepperMotor(15, 18, 17, 27)
	stepper.spin(475, speed=150)
	stepper.release()

def release():
	speed = 20
	x = Axis(2, 3, 4, 14, 37, 0.11, speed)
	y = Axis(15, 18, 17, 27, 41, 0.082, speed)

	x.release()
	y.release()

try:
	basicTest()

except:
	release()

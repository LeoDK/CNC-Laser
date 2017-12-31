# -*- coding:utf-8 -*-

from system2D import Machine, Axis
from laser import Laser
from time import sleep
import sys

################################################################################################
#############################                                        ###########################
############################# Défintion des propriétés de la machine ###########################
#############################                                        ###########################
################################################################################################

#La vitesse en mm/s
speed = 20
#Les axes
x = Axis(2, 3, 4, 14, 39, 0.11, speed)
y = Axis(15, 18, 17, 27, 39, 0.082, speed)
#Le laser
laser = Laser(22)
#La machine
machine = Machine(x, y, laser)


################################################################################################
#############################                                        ###########################
#############################           Fonctions diverses           ###########################
#############################                                        ###########################
################################################################################################

def search(line, char):
	""" Cherche le charactère sur la ligne et retourne le nombre après """
	char_location = line.index(char)+1
	i = char_location

	#En ascii, 48 : 0 et 57:9. Donc on arrête qd il y a plus de chiffres ni de points ni de signe
	while ( 47<ord(line[i])<58 or line[i] == '.' or line[i] == '-' ):
		i+=1

	return float(line[char_location:i])

def xyPosition(line):
	""" Retourne les coordonnées x et y (pour une commande G0 ou G1) """
	x = search(line, 'X')
	y = search(line, 'Y')
	return (x,y)


def ijPosition(line):
	""" Même chose que pour xyPosition, mais avec I et J (G02 et G03) """
	i = search(line, 'I')
	j = search(line, 'J')
	return (i,j)


def notYetImplError():
	print "Sorry, functionnality not implemented yet. Exiting..."


################################################################################################
#############################                                        ###########################
#############################     Execute le ficher GCode en arg     ###########################
#############################                                        ###########################
################################################################################################

def execGCode(filename, machine):
	

	try:
		f = open(filename, 'r')

		for l in f:
			#Si la ligne est vide
			if not l:
				pass

			#Instructions de position
			#Position absolue
			if l[0:3] == 'G90':
				print "Absolute position"
				machine.setAbsoluteMode()

			#Position relative
			elif l[0:3] == 'G91':
				print "Relative position"
				machine.setRelativeMode()

			#Unités -> pouces
			elif l[0:3] == 'G20':
				notYetImplError()
				break

			#Unités -> mm
			elif l[0:3] == 'G21':
				print "Working in mm"

			#Retour a l'origine
			elif l[0:3] == 'G28':
				#Un seul axe...
				if 'X' in l:
					machine.home(axis=machine.x_axis)
				if 'Y' in l:
					machine.home(axis=machine.y_axis)
				#... ou les deux si rien n'est précisé
				if 'X' not in l and 'Y' not in l:
					machine.home()

			#Pause
			elif l[0:3] == 'G4 ':
				#En secondes
				if 'S' in l:
					t = search('S', l)
					sleep(t)
				#En ms
				else:
					t = search('P', l)
					sleep(t*0.001)

			#Définition des coordonnées de l'origine
			elif l[0:3] == 'G92':
				notYetImplError()
				break

			#Mouvement linéaire
			elif l[0:3] == 'G0 ' or l[0:3] == 'G1 ' or l[0:3] == 'G01':
				if 'F' not in l:
					x,y = xyPosition(l)
					machine.linearMovement(x, y)

			#Interpolation circulaire
			elif l[0:3] == 'G02' or l[0:3] == 'G03':
				x,y = xyPosition(l)
				i,j = ijPosition(l)
				#Sens horaire
				if l[0:3] == 'G02':
					machine.circularInterpolation(x, y, i, j, -1)
				else:
					machine.circularInterpolation(x, y, i, j, 1)

			#Instructions du laser
			elif l[0:3] == 'M03':
				laser.on()

			elif l[0:3] == 'M05':
				laser.off()

			#Terminé
			elif l[0:3] == 'M02':
				break

	except IOError:
		print "Couldn't open the file {}".format(filename)

	laser.off()
	machine.release()

	print "Done"

try:
	if len(sys.argv) != 2:
		print "Usage : ./main.py [file]"
		raise TypeError
	gcode_file = sys.argv[1]
	execGCode(gcode_file, machine)
except:
	machine.release()

# -*- coding:utf-8 -*-

from steppers import StepperMotor
from math import cos, sin, acos, sqrt, pi


################################################################################################
#############################                                        ###########################
#############################                Classe Axis             ###########################
#############################                                        ###########################
################################################################################################

class Axis (StepperMotor):
	""" 
	Pour [a1], [a2], [b1], [b2] voir la classe StepperMotor.
	[max_pos] est la position max que l'on peut atteindre sur l'axe, donc on peut bouger dans un intervalle de [0; max_pos] mm
	[res] est la résolution du moteur utilisé, en mm/pas
	[speed] est la vitesse de l'axe, en mm/s
	"""
	def __init__(self, a1, a2, b1, b2, max_pos, res, speed):
		StepperMotor.__init__(self, a1, a2, b1, b2)
		self.pos = 0
		self.max_pos = max_pos
		self.res = res
		self.speed = speed
		#True = coordonnées absolues; False = coordonnées relatives
		self._absolute = False

	""" Ajoute [pos] a la postion actuelle. [pos] est en mm. """
	def _relMove(self, pos):
		#On s'approche le plus possible de la valeur donnée (on ne peut bouger que de multiples de res)
		steps = int( round(pos/self.res) )
		#La vraie position a laquelle on va
		self.pos += (steps * self.res)
		#Conversion de mm/s en pas/s
		speed_steps = 0
		if pos != 0 : speed_steps = self.speed * steps / pos
		self.spin(steps, speed=speed_steps)

	""" Pareil que _relMove, mais avec [pos] une position absolue """
	def _absMove(self, pos):
		d = pos-self.pos
		self._relMove(d)

	""" Relatif aux différents modes : absolu ou relatif """
	def move(self, pos):
		if pos > self.max_pos : return None
		if self._absolute == True and pos > 0:
			self._absMove(pos)
		else:
			if self.pos + pos > 0 : self._relMove(pos)

	def setAbsoluteMode(self):
		self._absolute = True

	def setRelativeMode(self):
		self._absolute = False


################################################################################################
#############################                                        ###########################
#############################                Classe Machine          ###########################
#############################                                        ###########################
################################################################################################

class Machine (object):
	"""
	La classe Machine permet de contrôler la position du pointeur laser
	"""

	def __init__(self, x_axis, y_axis):
		"""
		[x_axis] et [y_axis] sont des objets Axis
		[speed] est la vitesse des axes en mm/s
		"""
		self.x_axis = x_axis
		self.y_axis = y_axis
		self.setRelativeMode()

	def _relLinearMovement(self, x, y):
		""" 
		Permet de bouger d'un point A a un point B en ligne droite en bougeant -presque- les deux axes en même temps.
		[x] and [y] sont en mm, positions relatives
		"""
		if x > self.x_axis.max_pos or y > self.y_axis.max_pos : return None

		sign = lambda x : 1 if x>=0 else -1

		n_x = int(round(x / self.x_axis.res))
		n_y = int(round(y / self.y_axis.res))

		sign_x = sign(n_x)
		sign_y = sign(n_y)
		n_x = abs(n_x)
		n_y = abs(n_y)

		if n_x == 0:
			total = n_y**2
			n_x = n_y
			#Mettre [n_y] > [total] fait que l'axe x ne tourne pas
			n_y = total+1 

		elif n_y == 0:
			total = n_x**2
			n_y = n_x
			n_x = total+1

		else:
			total = n_x * n_y

		#La méthode suivante permet d'établir équitablement la répartition des moteurs
		for i in range(1, total+1):
			if i % n_x == 0:
				self.y_axis.move(self.y_axis.res * sign_y)
			if i % n_y == 0:
				self.x_axis.move(self.x_axis.res * sign_x)

	def _absLinearMovement(self, x, y):
		"""
		Même chose que _relLinearMovement mais avec des positions absolues
		"""
		self.setRelativeMode()

		x -= self.x_axis.pos
		y -= self.y_axis.pos

		self._relLinearMovement(x, y)

		self.setAbsoluteMode()

	def linearMovement(self, x, y):
		"""
		Fonction générale (à utiliser)
		"""
		if self._absolute:
			self._absLinearMovement(x, y)
		else: 
			self._relLinearMovement(x, y)


	def circularInterpolation(self, x, y, i, j, direction):
		"""
		Permet de faire une interpolation circulaire.
		[x], [y], [i], [j] sont en mm.
		[direction] est soit 1 (sens trigo), soit -1 (sens horaire)
		"""
		#A est le point de dépat
		if self._absolute:
			A = (self.x_axis.pos, self.y_axis.pos)
		else:
			A = (0, 0)

		#B est le point d'arrivee
		B = (x,y)

		#Omega est le centre du cercle d'interpolation
		w = (A[0]+i, A[1]+j)

		#Le rayon de ce cercle
		r = sqrt(i**2+j**2)

		"""
		Méthode :
		 - wA est le vecteur qui va du centre du cercle vers le point de départ
		 - wB est le vecteur qui va du centre du cercle vers le point d'arrivée
		 - wA' est le vecteur orthogonal a wA qui respecte le sens choisi ([direction] -> trigo ou horaire). wA et wA' forment une base.
		 - theta = (wA; wB)
		 - a l'aide des formules du produit scalaire de vecteurs, on déduit cos(theta)
		 - alpha = (wA'; wB)
		 - de mÃªme que pour cos(theta), on trouve cos(alpha)
		 - on en déduit sin(theta)
		 - on calcule l'angle theta, en fonction de la situation (direction, placement des points...)
		 - on déduit la longueur de l'arc de cerclea graver
		 - on calcule le nombre de mouvements linéares a effectuer
		 - pour chaque mouvement linéaire, on prend l'angle de l'arc de cercle, on trouve les coordonnées du point d'arrivée, et on y va
		"""

		wA = (-i, -j)
		wB = (B[0]-w[0], B[1]-w[1])
		wA_prime = (direction*j, -direction*i)

		#     -> ->   ->    ->      -> ->                    ->      ->
		#Comme u.v = ||u|| ||v|| cos(u; v) = xx'+yy' et que ||u|| = ||v|| = r
		cos_theta = (wA[0]*wB[0] + wA[1]*wB[1]) / r**2

		#On a theta = alpha+pi/2 (car wA et wA' sont orthogonaux). Donc sin(theta) = sin(alpha+pi/2) = cos(alpha)
		sin_theta = (wA_prime[0]*wB[0] + wA_prime[1]*wB[1]) / r**2

		#Erreurs
		if cos_theta > 1 : cos_theta = 1
		if cos_theta < -1 : cos_theta = -1

		theta = acos(cos_theta)

		#Comme python nous sort toujours un angle positif entre 0 et pi avec acos, il faut checker le signe de l'angle avec son sinus
		if sin_theta < 0:
			theta += pi

		#Longueur de l'arc de cercle a parcourir : d = (theta/(2*pi)) * 2pi*r = theta*r
		d = theta * r

		#Le nombre de mouvements linéaires
		nb_movements = int(round( d/max(self.x_axis.res, self.y_axis.res) ))

		for i in range(1, nb_movements+1):
			#N le prochain point a atteindre, tmp_theta est l'angle AwN
			tmp_theta = theta * i/nb_movements

			#Formules de base, se référer au cercle trigo
			tmp_x = wA[0] * cos(tmp_theta) + wA_prime[0] * sin(tmp_theta) + w[0]
			tmp_y = wA[1] * cos(tmp_theta) + wA_prime[1] * sin(tmp_theta) + w[1]

			self.linearMovement(tmp_x, tmp_y)


	def home(self, axis=None):
		""" Va à l'origine, un axe après l'autre pour simplifier. Si [axis] n'est pas précisé, on renvoie les deux axes à l'origine """
		if not axis:
			self.x_axis._absMove(0)
			self.y_axis._absMove(0)

		else:
			for a in axis:
				a._absMove(0)

	def release(self):
		""" Une fois l'opération terminée, pensea appeler cette fonction """
		self.home()
		self.x_axis.release()
		self.y_axis.release()

	def setAbsoluteMode(self):
		""" Passer en mode absolu """
		self.x_axis.setAbsoluteMode()
		self.y_axis.setAbsoluteMode()
		self._absolute = True
		
	def setRelativeMode(self):
		""" Passer en mode relatif """
		self.x_axis.setRelativeMode()
		self.y_axis.setRelativeMode()
		self._absolute = False

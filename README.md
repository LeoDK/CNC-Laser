# CNC-Laser
CNC Laser for RaspberryPi-based CNC laser machines.

This code was designed to easily control a 2 axis laser CNC machine with a Raspberry Pi (tested with model 1B).
It fits on a reclamation based CNC machine, made with 2 DVD engravers.

 * If you want to apply this code on a different machine, or on a different Raspberry (or Orange Pi 
and its derivatives) it's -normally- easy to modify the parameters for your machine.

 * If you want to make this Laser engraving machine -> http://www.instructables.com/id/Pocket-laser-engraver/
Normally this code just needs to be executed on a Raspberry, and only parameters defined in main.py need to 
be modified (pins, steppers speed, resolution, maximum position, etc...)

Enjoy!


main.py -> Contains all the configuration for a standard 2 axis machine on motors, etc...
steppers.py -> Low level stepper control
system2D.py -> Axis and CNC classes
laser.py -> Laser defintion

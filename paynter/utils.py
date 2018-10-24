#External modules
import numpy as N 
from numba import jit, float32, int64

#Python base libs
import random
import math
import colorsys

######################################################################
# Useful Functions
######################################################################
#Jitted functions for trigonometry
@jit(float32(float32, float32), nopython=True, cache=True)
def lendir_x(l, d):
	return l*N.cos(d)
@jit(float32(float32, float32), nopython=True, cache=True)
def lendir_y(l, d):
	return l*N.sin(d)

#Clamp shortcut
def clamp(x, mi, ma):
	return max(mi, min(ma, x))

#Random shortcut
def randInt(a,b):
	return random.randint(a,b) #inclusive

#Random shortcut
def randFloat(a,b):
	return random.uniform(a,b)

#Degree cosine shortcut
def dcos(deg):
	return math.cos(math.radians(deg))

#Degree sine shortcut
def dsin(deg):
	return math.sin(math.radians(deg))

#Get fuzzy
def fuzzy(fuzzyRange):
	return random.uniform(fuzzyRange[0], fuzzyRange[1])

#Rotate a list of points around a center for an angle
def rotateMatrix(pointList, cx, cy, angle):
	
	rotatedPoints = []
	#For each point in the list
	for point in pointList:
		#Grab the coords and get dir and len
		oldX = point[0]
		oldY = point[1]
		direction = math.degrees(math.atan2(cy-oldY, cx-oldX))
		length = math.sqrt((cx - oldX)**2 + (cy - oldY)**2)

		#Rotate them and insert in the return list
		newX = cx+length*dcos(direction+angle)
		newY = cy+length*dsin(direction+angle)
		rotatedPoints.append([newX, newY])
	return rotatedPoints

#Interpolate two points (pos=0 -> returns x1,y1; pos=1 -> return x2,y2)
def linearInterpolationPoint(x1,y1,x2,y2, pos):
    xx = x1+pos*(x2-x1)
    yy = y1+pos*(y2-y1)
    return (xx,yy)

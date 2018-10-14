#External modules
import numpy as N 

#Python base libs
import random
import math
import colorsys

######################################################################
# Useful Functions
######################################################################

#Take 0-1 hsv and outputs a 0-1 rgb
def hsv2rgb(hsv):
    return N.asarray(colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))

#Take 0-1 rgb and outputs 0-1 hsv
def rgb2hsv(rgb):
    return N.asarray(colorsys.rgb_to_hsv(rgb[0],rgb[1],rgb[2]))

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
	return randFloat(fuzzyRange[0], fuzzyRange[1])

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
		newX = cx+length*dcos(direction+math.radians(angle))
		newY = cy+length*dsin(direction+math.radians(angle))
		rotatedPoints.append([newX, newY])
	return rotatedPoints


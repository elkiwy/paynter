#PaYnter Modules
from .utils import *

import sys
import colorsys


######################################################################
# Color Management functions
######################################################################
#Get 3 colors with a triad pattern
def getColors_Triad(sat = 1, val = 1, spread = 60):
	palette = list()
	leadHue = randFloat(0, 1)
	palette.append(Color([leadHue, sat, val], 'hsv'))
	palette.append(Color([(leadHue + 0.5 + spread/360) % 1, sat, val], 'hsv'))
	palette.append(Color([(leadHue + 0.5 - spread/360) % 1, sat, val], 'hsv'))	
	return palette 



#Colors are always internally stored as 0-1 floats
class Color:
	r, g, b, a = 0, 0, 0, 0

	def __init__(self, val, mode):
		if mode=='0-255':
			self.r = val[0]/255
			self.g = val[1]/255
			self.b = val[2]/255
			self.a = val[3]/255
		elif mode=='0-1':
			self.r = val[0]
			self.g = val[1]
			self.b = val[2]
			self.a = val[3]
		elif mode=='hex':
			val = val.lstrip('#')
			if len(val)!=6:
				print('ERROR: Trying to create a color with bad hex: '+str(mode)+' supported hex are like: #ff00ff only')
				sys.exit()
			self.r = int(val[0:2], 16)
			self.g = int(val[2:4], 16)
			self.b = int(val[4:6], 16)
			self.a = 1
		elif mode=='hsv':
		    rgb = colorsys.hsv_to_rgb(val[0],val[1],val[2])
		    self.r = rgb[0]
		    self.g = rgb[1]
		    self.b = rgb[2]
		    self.a = 1
		else:
			print('ERROR: Trying to create a color with unrecognized mode: '+str(mode)+' supported modes are: "0-255", "0-1", "hex", "hsv"')
			sys.exit()

	#Return 0-255 RGBA
	def get_0_255(self):
		return [self.r*255, self.g*255, self.b*255, self.a*255]

	#Return 0-1 RGBA
	def get_0_1(self):
		return [self.r, self.g, self.b, self.a]

	#Returns 0-1 HSV
	def get_HSV(self):
	    return N.asarray(colorsys.rgb_to_hsv(self.r, self.g, self.b))

	#Overwrite RGB values with this HSV
	def set_HSV(self, hsv):
	    rgb = colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2])
	    self.r = rgb[0]
	    self.g = rgb[1]
	    self.b = rgb[2]

	#Sets a new alpha value
	def set_alpha(self, newAlpha):
		if newAlpha>=0 and newAlpha<=1:
			self.a = newAlpha
		else:
			print('ERROR: Color::set_alpha only supports 0-1 values, got: '+str(mode))
			sys.exit()

	#Tweak the hue
	def tweak_Hue(self, ammount):
		hsv = self.get_HSV()
		hsv[0] = (hsv[0] + ammount) % 1
		self.set_HSV(hsv)

	#Tweak the saturation
	def tweak_Sat(self, ammount):
		hsv = self.get_HSV()
		hsv[1] = clamp(hsv[1] + ammount, 0, 1)
		self.set_HSV(hsv)
		
	#Tweak the value
	def tweak_Val(self, ammount):
		hsv = self.get_HSV()
		hsv[2] = clamp(hsv[2] + ammount, 0, 1)
		self.set_HSV(hsv)

	def copy(self):
		return Color([self.r, self.g, self.b, self.a], '0-1')
		





















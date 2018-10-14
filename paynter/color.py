#PaYnter Modules
from .utils import *


######################################################################
# Color Management functions
######################################################################
#Get 3 colors with a triad pattern
def getColors_Triad(sat = 1, val = 1, spread = 60):
	palette = list()
	leadHue = randFloat(0, 1)

	#First color
	hsv = [	leadHue, sat, val]
	rgb = hsv2rgb(hsv)*255
	rgba = [rgb[0], rgb[1], rgb[2], 255]
	palette.append(rgba)

	#Second color
	hsv = [	(leadHue + 0.5 + spread/360) % 1, sat, val]
	rgb = hsv2rgb(hsv)*255
	rgba = [rgb[0], rgb[1], rgb[2], 255]
	palette.append(rgba)

	#Third
	hsv = [	(leadHue + 0.5 - spread/360) % 1, sat, val]
	rgb = hsv2rgb(hsv)*255
	rgba = [rgb[0], rgb[1], rgb[2], 255]
	palette.append(rgba)

	return palette 

#Change the hue of a color
def tweakColorHue(rgba, ammount):
	hsv = rgb2hsv(N.asarray(rgba[:3])/255)
	hsv[0] = (hsv[0] + ammount) % 1
	rgba[:3] = hsv2rgb(hsv)
	rgba[0] *= 255
	rgba[1] *= 255
	rgba[2] *= 255
	return rgba

#Change the saturation of a color
def tweakColorSat(rgba, ammount):
	hsv = rgb2hsv(N.asarray(rgba[:3])/255)
	hsv[1] = clamp(hsv[1] + ammount, 0, 1)
	rgba[:3] = hsv2rgb(hsv)
	rgba[0] *= 255
	rgba[1] *= 255
	rgba[2] *= 255
	return rgba

#Change the value of a color
def tweakColorVal(rgba, ammount):
	print(rgba)
	hsv = rgb2hsv(N.asarray(rgba[:3])/255)
	hsv[2] = clamp(hsv[2] + ammount, 0, 1)
	rgba[:3] = hsv2rgb(hsv)
	rgba[0] *= 255
	rgba[1] *= 255
	rgba[2] *= 255
	return rgba




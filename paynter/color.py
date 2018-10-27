#PaYnter Modules
from .utils import *
from numba import jitclass, float32, float64

import sys







@jit([float32[:](float32, float32, float32)], nopython=True)
def rgb_to_hsv(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    if minc == maxc:
        return N.array((0.0, 0.0, v), dtype=N.float32)
    s = (maxc-minc) / maxc
    rc = (maxc-r) / (maxc-minc)
    gc = (maxc-g) / (maxc-minc)
    bc = (maxc-b) / (maxc-minc)
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    return N.array((h, s, v), dtype=N.float32)

@jit(float32[:](float32, float32, float32), nopython=True)
def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return N.array((v, v, v), dtype=N.float32)
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return N.array((v, t, p), dtype=N.float32)
    if i == 1:
        return N.array((q, v, p), dtype=N.float32)
    if i == 2:
        return N.array((p, v, t), dtype=N.float32)
    if i == 3:
        return N.array((p, q, v), dtype=N.float32)
    if i == 4:
        return N.array((t, p, v), dtype=N.float32)
    if i == 5:
        return N.array((v, p, q), dtype=N.float32)
    return N.array((0,0,0), dtype=N.float32)




######################################################################
# Color Management functions
######################################################################
#Get 3 colors with a triad pattern
def getColors_Triad(sat = 1, val = 1, spread = 60):
	palette = list()
	leadHue = randFloat(0, 1)
	palette.append(Color(0,0,0,1).set_HSV(leadHue, sat, val))
	palette.append(Color(0,0,0,1).set_HSV((leadHue + 0.5 + spread/360) % 1, sat, val))
	palette.append(Color(0,0,0,1).set_HSV((leadHue + 0.5 - spread/360) % 1, sat, val))	
	return palette 



#Colors are always internally stored as 0-1 floats
spec = [
    ('r', float32),
    ('g', float32),
    ('b', float32),
    ('a', float32)
]

@jitclass(spec)
class Color:
	def __init__(self, r, g, b, a):
		if max((r,g,b,a))>1:
			r /= 255
			b /= 255
			g /= 255
			a /= 255

		self.r = r
		self.g = g
		self.b = b
		self.a = a

	#Return 0-255 RGBA
	def get_0_255(self):
		return [self.r*255, self.g*255, self.b*255, self.a*255]

	#Return 0-1 RGBA
	def get_0_1(self):
		return N.array((self.r, self.g, self.b, self.a), dtype=N.float32)

	#Returns 0-1 HSV
	def get_HSV(self):
	    return rgb_to_hsv(self.r, self.g, self.b)

	#Overwrite RGB values with this HSV
	def set_HSV(self, h, s, v):
		rgb = hsv_to_rgb(h,s,v)
		self.r = rgb[0]
		self.g = rgb[1]
		self.b = rgb[2]
		return self

	#Sets a new alpha value
	def set_alpha(self, newAlpha):
		self.a = newAlpha
		return self

	#Gets the alpha value
	def get_alpha(self):
		return self.a

	#Tweak the hue
	def tweak_Hue(self, ammount):
		hsv = self.get_HSV()
		hsv[0] = (hsv[0] + ammount) % 1
		self.set_HSV(hsv[0], hsv[1], hsv[2])
		return self

	#Tweak the saturation
	def tweak_Sat(self, ammount):
		hsv = self.get_HSV()
		hsv[1] = min(max(hsv[1] + ammount, 0), 1)
		self.set_HSV(hsv[0], hsv[1], hsv[2])
		return self
		
	#Tweak the value
	def tweak_Val(self, ammount):
		hsv = self.get_HSV()
		hsv[2] = min(max(hsv[2] + ammount, 0), 1)
		self.set_HSV(hsv[0], hsv[1], hsv[2])
		return self

	def copy(self):
		return Color(self.r, self.g, self.b, self.a)
		





















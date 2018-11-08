"""
The Color class is another fundamental class in the Paynter library.
This module will mange the creation, modification, and storing of colors and palettes.

The color class is mainly used internally by the :py:class:`Paynter` class, but the user will still have to create the palette and sets the active colors manually through Paynter.setColor(color).
"""

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
def getColors_Triad(hue=None, sat = 1, val = 1, spread = 60):
	"""
	Create a palette with one main color and two opposite color evenly spread apart from the main one. 

	:param hue: A 0-1 float with the starting hue value.
	:param sat: A 0-1 float with the palette saturation.
	:param val: A 0-1 float with the palette value.
	:param val: An int with the spread in degrees from the opposite color.
	:rtype: A list of :py:class:`Color` objects.
	"""
	palette = list()
	if hue==None:
		leadHue = randFloat(0, 1)
	else:
		leadHue = hue
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
	"""
	The :py:class:`Color` class has 4 0-1 floats, one for each RGBA channel.

	A Color class is created from palette functions or directly with their constructor.

	.. code-block:: python

		from paynter import *
		
		#Get a list of colors
		palette = getColors_Triad(spread = 20)

		#You can create with 0-1 floats..
		otherColor = Color(1, 0.5, 0, 1)

		#.. or with 0-255 ints
		sameColor = Color(255, 128, 0, 255)
	"""
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
		"""
		Gets the RGBA 0-255 rappresentation of this color.

		:rtype: A list of 4 ints.
		"""
		return [self.r*255, self.g*255, self.b*255, self.a*255]

	#Return 0-1 RGBA
	def get_0_1(self):
		"""
		Gets the RGBA 0-1 rappresentation of this color.

		:rtype: A list of 4 floats.
		"""
		return N.array((self.r, self.g, self.b, self.a), dtype=N.float32)

	#Returns 0-1 HSV
	def get_HSV(self):
		"""
		Gets the HSV 0-1 rappresentation of this color.
		This does ignore the alpha value.

		:rtype: A list of 3 floats.
		"""
		return rgb_to_hsv(self.r, self.g, self.b)

	#Overwrite RGB values with this HSV
	def set_HSV(self, h, s, v):
		"""
		Overwrite the current color with this set of HSV values.
		This keeps the current alpha value.
		
		:param h: A 0-1 float with the Hue.
		:param s: A 0-1 float with the Saturation.
		:param v: A 0-1 float with the Value.
		:rtype: The new :py:class:`Color` object.
		"""
		rgb = hsv_to_rgb(h,s,v)
		self.r = rgb[0]
		self.g = rgb[1]
		self.b = rgb[2]
		return self

	#Sets a new alpha value
	def set_alpha(self, newAlpha):
		"""
		Overwrite the current alpha value.
		
		:param newAlpha: A 0-1 float with the desired alpha.
		:rtype: The :py:class:`Color` object.
		"""
		self.a = newAlpha
		return self

	#Gets the alpha value
	def get_alpha(self):
		"""
		Gets the current alpha value.

		:rtype: A 0-1 float.
		"""
		return self.a

	#Tweak the hue
	def tweak_Hue(self, ammount):
		"""
		Change the current hue value by a certain ammount.

		:param ammount: A 0-1 float with the ammount to sum to the current hue.
		:rtype: The :py:class:`Color` object.
		"""
		hsv = self.get_HSV()
		hsv[0] = (hsv[0] + ammount) % 1
		self.set_HSV(hsv[0], hsv[1], hsv[2])
		return self

	#Tweak the saturation
	def tweak_Sat(self, ammount):
		"""
		Change the current saturation value by a certain ammount.

		:param ammount: A 0-1 float with the ammount to sum to the current saturation.
		:rtype: The :py:class:`Color` object.
		"""
		hsv = self.get_HSV()
		hsv[1] = min(max(hsv[1] + ammount, 0), 1)
		self.set_HSV(hsv[0], hsv[1], hsv[2])
		return self
		
	#Tweak the value
	def tweak_Val(self, ammount):
		"""
		Change the current value value by a certain ammount.

		:param ammount: A 0-1 float with the ammount to sum to the current value.
		:rtype: The :py:class:`Color` object.
		"""
		hsv = self.get_HSV()
		hsv[2] = min(max(hsv[2] + ammount, 0), 1)
		self.set_HSV(hsv[0], hsv[1], hsv[2])
		return self

	def copy(self):
		"""
		Creates a copy of this Color.

		:rtype: The new :py:class:`Color` object.
		"""
		return Color(self.r, self.g, self.b, self.a)
		





















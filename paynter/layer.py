"""
This is the class that compose the :py:class:`Image` objects.
This module will take care of storing data as 3D arrays of uint8.
The array dimension are width, height, and RGBA channels of that layer.

This class will be 100% managed through the :py:class`Paynter` class, so you should never instantiate it manually.
"""

#External modules
import numpy as N
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

#PaYnter Modules
import paynter.config as config
from .color import *

######################################################################
# Layer Functions
######################################################################
#The layer class the the one holding all the data and effecct to show how to add colors when merging layers
class Layer:
	"""
	The :py:class:`Layer` class contains a 3D array of N.uint8 and a string with the blend mode of the layer.

	An Image starts with one layer inside, but you can create more of them as follows:

	.. code-block:: python

		from paynter import *

		#Inside the paynter there is already an Image with a blank Layer.
		paynter = Paynter()
		
		#Create a blank new layer
		payner.newLayer()

		#Create a new layer duplicating the current one
		payner.duplicateActiveLayer()

		#Gets the current active layer		
		layer = paynter.image.getActiveLayer()
	"""
	effect = ''
	data = 0

	#Layer constructor
	# Layers data structure are always 0-255 ints
	def __init__(self, data = None, color = None, effect = ''):
		if type(data) is not N.ndarray:
			self.data = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE, 4), dtype=N.uint8)
			if color==None:
				color = Color(0,0,0,0)
			colorRGBA = color.get_0_255()
			self.data[:,:,0] = colorRGBA[0]
			self.data[:,:,1] = colorRGBA[1]
			self.data[:,:,2] = colorRGBA[2]
			self.data[:,:,3] = colorRGBA[3]
		else:
			self.data = data
		self.effect = effect

	#Show layer as a separate image with the option to write on it 
	def showLayer(self, title='', debugText=''):
		"""
		Shows the single layer.
		
		:param title: A string with the title of the window where to render the image.
		:param debugText: A string with some text to render over the image.
		:rtype: Nothing.
		"""
		img = PIL.Image.fromarray(self.data, 'RGBA')
		if debugText!='':
			draw = PIL.ImageDraw.Draw(img)
			font = PIL.ImageFont.truetype("DejaVuSansMono.ttf", 24)
			draw.text((0, 0),debugText,(255,255,255),font=font)
		img.show(title=title)

#External modules
import numpy as N
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

#PaYnter Modules
import paynter.config as config
from .color import Color

######################################################################
# Layer Functions
######################################################################
#The layer class the the one holding all the data and effecct to show how to add colors when merging layers
class Layer:
	effect = ''
	data = 0

	#Layer constructor
	# Layers data structure are always 0-255 ints
	def __init__(self, data = None, color = None, effect = ''):
		if type(data) is not N.ndarray:
			self.data = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE, 4), dtype=N.uint8)
			if color==None:
				color = Color(1,1,1,0)
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
		img = PIL.Image.fromarray(self.data, 'RGBA')
		if debugText!='':
			draw = PIL.ImageDraw.Draw(img)
			font = PIL.ImageFont.truetype("DejaVuSansMono.ttf", 24)
			draw.text((0, 0),debugText,(255,255,255),font=font)
		img.show(title=title)

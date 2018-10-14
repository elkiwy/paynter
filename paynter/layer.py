#External modules
import numpy as N
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

#PaYnter Modules
import paynter.config as config

######################################################################
# Layer Functions
######################################################################
#The layer class the the one holding all the data and effecct to show how to add colors when merging layers
class Layer:
	effect = ''
	data = 0

	#Layer constructor
	def __init__(self, data = None, color = [255,255,255,0], effect = ''):
		if type(data) is not N.ndarray:
			self.data = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE, 4), dtype=N.uint8)
			self.data[:,:,0] = color[0]
			self.data[:,:,1] = color[1]
			self.data[:,:,2] = color[2]
			self.data[:,:,3] = color[3]
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

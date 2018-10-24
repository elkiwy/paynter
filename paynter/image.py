#External modules
import PIL.Image 
import numpy as N

#PaYnter Modules
from .layer import Layer
from .blendModes import *

######################################################################
# Image Functions
######################################################################
#The image class is a container for all the layers of the image
class Image:
	layers = []
	activeLayer = 0

	#Init image
	def __init__(self):
		#Init by adding a new layer and selecting that as current layer
		self.layers.append(Layer())
		self.activeLayer = len(self.layers)-1

	#Return the current active layer
	def getActiveLayer(self):
		return self.layers[self.activeLayer]

	#Create a new layer and select it
	def newLayer(self, effect=''):
		self.layers.append(Layer(effect = effect))
		self.activeLayer = len(self.layers)-1

	#Duplicate the current layer
	def duplicateActiveLayer(self):
		activeLayer = self.layers[self.activeLayer]
		newLayer = Layer(data=activeLayer.data, effect=activeLayer.effect)
		self.layers.append(newLayer)
		self.activeLayer = len(self.layers)-1

	#Merge all the layers together to render the final image
	def mergeAllLayers(self):
		while(len(self.layers)>1):
			self.mergeBottomLayers()
		return self.layers[0]

	#Merge the bottom layer with the layer above that
	def mergeBottomLayers(self):
		#Debug show the two layer being merged
		print('merging layers with:'+str(self.layers[1].effect))
	
		#Normal paste on top
		if self.layers[1].effect=='':
			baseImage = PIL.Image.fromarray(self.layers[0].data, 'RGBA')
			overImage = PIL.Image.fromarray(self.layers[1].data, 'RGBA')
			baseImage = PIL.Image.alpha_composite(baseImage, overImage)
			newImage = N.array(baseImage)

		#Apply blend mode
		else:
			baseImage = self.layers[0].data.astype(N.float32)
			overImage = self.layers[1].data.astype(N.float32)
			newImage = mergeImagesWithBlendMode(baseImage, overImage, self.layers[1].effect).astype(N.uint8)

		#Remove one layer and replace the last one
		del self.layers[0]			
		self.layers[0] = Layer(data = newImage)

	
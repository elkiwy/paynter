"""
Another key class inside the Paynter library is the Image class.
This module will take care of storing all the layers data of the current image you are creating.
It will also manage to merge all the layer during the final rendering process.

This class will normally be 100% managed through the :py:class`Paynter` class, so you should never instantiate it manually.
"""
#External modules
import PIL.Image 
import numpy as N

#PaYnter Modules
from .layer import Layer
from .blendModes import *

import time

######################################################################
# Image Functions
######################################################################
#The image class is a container for all the layers of the image
class Image:
	"""
	The :py:class:`Image` class is structured as an array of :py:class:`Layer`.

	An Image class is created when you create a :py:class:`Paynter`, so you can access this class as follows:

	.. code-block:: python

		from paynter import *
		
		paynter = Paynter()
		image = paynter.image
	"""
	layers = []
	activeLayer = 0

	#Init image
	def __init__(self):
		#Init by adding a new layer and selecting that as current layer
		self.layers.append(Layer())
		self.activeLayer = len(self.layers)-1

	#Return the current active layer
	def getActiveLayer(self):
		"""
		Returns the currently active :py:class:`Layer`.
		
		:rtype: A :py:class:`Layer` object.
		"""
		return self.layers[self.activeLayer]

	#Create a new layer and select it
	def newLayer(self, effect=''):
		"""
		Creates a new :py:class:`Layer` and set that as the active.
		
		:param effect: A string with the blend mode for that layer that will be used when during the rendering process. The accepted values are: :code:`'soft_light','lighten','screen','dodge','addition','darken','multiply','hard_light','difference','subtract','grain_extract','grain_merge','divide','overlay'`.
		:rtype: Nothing.
		"""
		self.layers.append(Layer(effect = effect))
		self.activeLayer = len(self.layers)-1

	#Duplicate the current layer
	def duplicateActiveLayer(self):
		"""
		Duplicates the current active :py:class:`Layer`.
		
		:rtype: Nothing.
		"""
		activeLayer = self.layers[self.activeLayer]
		newLayer = Layer(data=activeLayer.data, effect=activeLayer.effect)
		self.layers.append(newLayer)
		self.activeLayer = len(self.layers)-1

	#Merge all the layers together to render the final image
	def mergeAllLayers(self):
		"""
		Merge all the layers together.

		:rtype: The result :py:class:`Layer` object. 
		"""
		start = time.time()
		while(len(self.layers)>1):
			self.mergeBottomLayers()
		print('merge time:'+str(time.time()-start))
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

	
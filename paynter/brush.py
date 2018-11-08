"""
The second most important module of the PaYnter project.
This module will manage all the data relative to the brushes you will create and use inside your scripts.

The :py:class:`Brush` is a quite complex class in the insides, but luckly the Paynter manages all the drawing.
So the final user of the library needs only to instantiate one (or more) brush and pass it to his :py:class:`Paynter`.
"""

#External modules
import PIL.Image
import numpy as N
from numba import jit, int32, float32, int64, float64, uint8, void

#PaYnter Modules
import paynter.config as config
from .utils import *
from .color import *

import time

######################################################################
# Brush class
######################################################################
resizeResample = PIL.Image.LANCZOS
rotateResample = PIL.Image.BICUBIC

#Image to brushtip function
def loadBrushTip(path, size, angle):
	#Open the image and make sure its RGB
	res = PIL.Image.open(config.ROOT+'/res/'+path).convert('RGB')
	
	#Resize it to the target size
	resScaled = res.resize((size, size), resample=resizeResample)
	
	#Invert and grab the value
	resScaled = PIL.ImageOps.invert(resScaled)
	resScaled = resScaled.rotate(angle, expand = 1)
	grayscaleValue = resScaled.split()[0]

	#Create the brushtip image
	bt = N.zeros((resScaled.width, resScaled.height, 4), dtype=N.float32)
	bt[:,:,0] = 1
	bt[:,:,1] = 1
	bt[:,:,2] = 1		
	bt[:,:,3] = N.divide(N.array(grayscaleValue), 255)

	#Return this 3D array full white and alpha 0-1 values
	return bt

#The brush class is the one that define how the current brush should behave
class Brush:
	"""
	The :py:class:`Brush` class is the one that defines how your Paynter should draw his lines.
	To create this class you can use the default constructor.
	   
	.. code-block:: python

		from paynter import *
		pixelBrush = Brush( "pixel.png", "", size = 100, spacing = 1)
	"""
	brushTip = 0
	brushMask = 0
	brushSize = 0
	multibrush = False
	spacing = 0
	fuzzyDabAngle = 0
	fuzzyDabSize = 0
	fuzzyDabHue = 0
	fuzzyDabSat = 0
	fuzzyDabVal = 0
	fuzzyDabMix = 0
	fuzzyDabScatter = 0
	originalSpacing = 0
	originalSize = 0
	realCurrentSize = 0
	coloredBrushSource = None 
	usesSourceCaching = False

	#Create the brush
	def __init__(self, tipImage, maskImage, size = 50, angle = 0, spacing = 1, 
				fuzzyDabAngle = 0, fuzzyDabSize = 0, fuzzyDabHue = 0, fuzzyDabSat = 0, fuzzyDabVal = 0, fuzzyDabMix = 0,
				fuzzyDabScatter = 0, usesSourceCaching = False):
		"""
		The creation of a :py:class:`Brush` can be as simple as the example above or pretty complex.
		The complexity is based on what effect you want to obtain from your Brush.
		There are a lot of parameters that you can define to customize your Brush the way you want to be.

		This is an example of a complex brush that emulates a watercolour brush:

		.. code-block:: python
		
			watercolor = Brush(["watercolor1.png","watercolor2.png","watercolor3.png","watercolor4.png","watercolor5.png"], # Use more than a single brush tip image to create more randomization
						"",				# No texture for this brush
						size = 440,			# Quite big brush
						angle = 0,			# No angle since we randomize it later each dab
						spacing = 0.5,			# Spacing to half the size of the brush
						fuzzyDabAngle = [0, 360],	# Randomize angle each dab
						fuzzyDabSize = [1, 2],		# Randomize the size of each dab between original size and double the size
						fuzzyDabHue = [-0.03, 0.03],	# Randomize slightly the hue of each dab
						fuzzyDabSat = [-0.2, 0.2],	# Randomize slightly the saturation of each dab
						fuzzyDabVal = [-0.1, 0.1],	# Randomize slightly the value of each dab
						fuzzyDabMix = [0.4, 0.5],	# Randomize slightly the mix of each dab
						fuzzyDabScatter = [0, 100])	# Make each dab go a bit of the trail to create more randomization


		:param tipImage: A string with the path of the image that you want to use as a tip. 
		                 If you want to load multiple brush tips and randomize between them each dab, you can place a list of strings instead.
		:param maskImage: A string with the path of the image that you want to use as a texture to apply to your brush.
		:param size: An integer with the size in pixel of the brush.
		:param angle: An integer with the angle (degrees) of the brush.
		:param spacing: A float with the spacing of the brush. Spacing is tells the system how far apart are each brush dab is. 
		                The value of this parameter is proportional to the brush size.
		:param fuzzyDabAngle: A list of two integers with the range between randomize the brush angle (degrees) of each dab. 
		:param fuzzyDabSize: A list of two numbers with the range between randomize the brush size (in a proportional way to the current brush size) of each dab.  
		:param fuzzyDabHue: A list of two float with the range between randomize the hue of each dab.
		:param fuzzyDabSat: A list of two float with the range between randomize the saturation of each dab.
		:param fuzzyDabVal: A list of two float with the range between randomize the value of each dab.
		:param fuzzyDabMix: A list of two float with the range between randomize the mix of each dab.
		:param fuzzyDabScatter: A list of two numbers with the range between randomize the deviation from the actual coordinates of each dab.
		:param usesSourceCaching: A boolean telling the system if he can cache the brush dab for much faster consecutives dab. 
		                          Not advised when the brush has fuzzy dab parameters.
		"""


		#Downsample the size-related parameters
		self.originalSize = size
		self.realCurrentSize = size
		size = int(size/config.DOWNSAMPLING)
		if fuzzyDabScatter!=0:
			fuzzyDabScatter[0] = int(fuzzyDabScatter[0]/config.DOWNSAMPLING)
			fuzzyDabScatter[1] = int(fuzzyDabScatter[1]/config.DOWNSAMPLING)

		#Set the brushTip
		if isinstance(tipImage, list):
			#Multibrush
			self.brushTip = []
			for image in tipImage:
				bt = loadBrushTip(image, size, angle)
				self.brushTip.append(bt)
			self.multibrush = True
			self.brushSize = self.brushTip[0].shape[0]
		else:
			#NormalBrush
			self.brushTip = loadBrushTip(tipImage, size, angle)
			self.brushSize = self.brushTip.shape[0]
		
		#Set the perameters
		self.spacing = size*spacing
		self.originalSpacing = spacing
		self.fuzzyDabAngle = fuzzyDabAngle
		self.fuzzyDabSize = fuzzyDabSize
		self.fuzzyDabHue = fuzzyDabHue
		self.fuzzyDabSat = fuzzyDabSat
		self.fuzzyDabVal = fuzzyDabVal
		self.fuzzyDabMix = fuzzyDabMix
		self.fuzzyDabScatter = fuzzyDabScatter
		self.usesSourceCaching = usesSourceCaching

		#Set the brush mask
		if maskImage!="":
			res = PIL.Image.open(config.ROOT+'/res/'+maskImage)
			while res.width>config.CANVAS_SIZE:
				res = res.resize((int(res.width/2),int(res.width/2)), resample=resizeResample)
			alpha = res.split()[0] #Take only the first channel since is black and white
			bm = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE), dtype=N.float32)
			for j in range(0, config.CANVAS_SIZE, res.width):
				for i in range(0, config.CANVAS_SIZE, res.width):
					bm[i:i+res.width, j:j+res.width] = N.divide(N.array(alpha), 255)
			self.brushMask = 1-bm
		
		else:
			#Add default mask
			bm = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE), dtype=N.float32)
			bm[:,:] = 0
			self.brushMask = 1-bm

	#Get the usesSourceCaching
	def doesUseSourceCaching(self):
		return self.usesSourceCaching

	#Cache the brush to save processing time
	def cacheBrush(self, color):
		self.coloredBrushSource = self.brushTip[:,:] * color.get_0_1()

	#Resize brush
	def resizeBrush(self, newSize):
		#Check if I want to reset back to original
		if newSize==0:
			newSize = self.originalSize

		#Don't do useless calculations
		if self.realCurrentSize == newSize:
			return

		#Downsample the size-related parameters
		print('resizing from :'+str(self.realCurrentSize)+' to:'+str(newSize))
		self.realCurrentSize = newSize
		newSize = max(int(newSize/config.DOWNSAMPLING), 1)

		#Set the brushTip
		if self.multibrush:
			#Multibrush
			for i in range(0,len(self.brushTip)):
				btImg = PIL.Image.fromarray((self.brushTip[i]*255).astype(N.uint8), 'RGBA')
				btImgScaled = btImg.resize((newSize, newSize), resample=resizeResample)
				btArray = N.divide(N.array(btImgScaled).astype(N.float32), 255)
				self.brushTip[i] = btArray
			self.brushSize = self.brushTip[0].shape[0]
		else:
			#NormalBrush
			btImg = PIL.Image.fromarray((self.brushTip*255).astype(N.uint8), 'RGBA')
			btImgScaled = btImg.resize((newSize, newSize), resample=resizeResample)
			btArray = N.divide(N.array(btImgScaled).astype(N.float32), 255)
			self.brushTip = btArray
			self.brushSize = self.brushTip.shape[0]
		
		#Set the perameters
		self.spacing = newSize*self.originalSpacing

	#Prepare a dab before the applyDab function, triggered only on brushes that do NOT use sourceCaching since each dab has different source on those
	def prepareDab(self, color, secondColor):
		#Get the brush image image 
		brushSource = self.brushTip if not self.multibrush else self.brushTip[randInt(0,len(self.brushTip)-1)]

		#Apply transformations
		if self.fuzzyDabAngle!=0 or self.fuzzyDabSize!=0:
			#Convert the brush to an image to ease out the rotation and resizing process
			img = PIL.Image.fromarray((brushSource*255).astype(N.uint8), 'RGBA')
			
			#Apply fuzzy scale
			if self.fuzzyDabAngle!=0:
				img = img.rotate(fuzzy(self.fuzzyDabAngle), expand=1, resample=PIL.Image.BILINEAR)
		
			#Apply fuzzy scale
			if self.fuzzyDabSize!=0:
				fuz = fuzzy(self.fuzzyDabSize)
				img = img.resize((int(img.width*fuz), int(img.height*fuz)), resample=PIL.Image.BILINEAR)
			
			#Reconvert brushSource to an array
			brushSource = N.array(img, dtype=N.float32)*0.0039

		if self.fuzzyDabHue!=0 or self.fuzzyDabSat!=0 or self.fuzzyDabVal!=0 or self.fuzzyDabMix!=0:
			#Apply fuzzy color transformations
			tmpColor = color.copy()
			
			#Mix colors
			if self.fuzzyDabMix!=0:
				fuz = fuzzy(self.fuzzyDabMix)
				tmpColor.r = min(1, (tmpColor.r*(1-fuz) + secondColor.r*fuz))
				tmpColor.g = min(1, (tmpColor.g*(1-fuz) + secondColor.g*fuz))
				tmpColor.b = min(1, (tmpColor.b*(1-fuz) + secondColor.b*fuz))
				
			#Fuzzy Hue
			if self.fuzzyDabHue!=0:
				tmpColor.tweak_Hue(fuzzy(self.fuzzyDabHue))

			#Fuzzy Saturation
			if self.fuzzyDabSat!=0:
				tmpColor.tweak_Sat(fuzzy(self.fuzzyDabSat))

			#Fuzzy Value
			if self.fuzzyDabVal!=0:
				tmpColor.tweak_Val(fuzzy(self.fuzzyDabVal))

			color = tmpColor

		#Color the brush
		return brushSource[:,:] * color.get_0_1()

	#Make a single dab on the canvas
	def makeDab(self, layer, x, y, color, secondColor, mirror=0):
		#Prepare the dab only if i don't have source caching
		if not self.usesSourceCaching:
			#Prepare the dab with all the fuzzy parameters 
			self.coloredBrushSource = self.prepareDab(color, secondColor)

		#Apply scattering if any
		if self.fuzzyDabScatter != 0:
			randomAngle = random.uniform(0,6.28)
			randomLength = fuzzy(self.fuzzyDabScatter)
			x += N.cos(randomAngle)*randomLength
			y += N.sin(randomAngle)*randomLength

		#Use the Jitted version to optimized calculus
		applyMirroredDab_jit(mirror, layer.data, int(x-self.brushSize*0.5), int(y-self.brushSize*0.5), self.coloredBrushSource.copy(), config.CANVAS_SIZE, self.brushMask)
		

#Jitted version of applyDab
@jit(void(uint8[:,:,:], int64, int64, float32[:,:,:], int64, float32[:,:]), nopython=True, cache=True)
def applyDab_jit(layerData, x, y, source, canvSize, brushMask):
	#Get the final dab size
	dabSizeX, dabSizeY = source.shape[:2]
	
	#Adjust coordinates and make sure we are inside (at least partially) the canvas
	adj_x1, adj_y1 = int(max(0, min(canvSize, x))), 			int(max(0, min(canvSize, y)))
	adj_x2, adj_y2 = int(max(0, min(canvSize, x+dabSizeX))), 	int(max(0, min(canvSize, y+dabSizeY)))
	if adj_x1==adj_x2 or adj_y1==adj_y2:return
	
	#Get the slice and uniform to [0-1]
	destination = N.divide(N.copy(layerData[adj_y1:adj_y2, adj_x1:adj_x2].astype(N.float32)), 255)
	
	#Calculate the correct range to make sure it works even on canvas border 
	bx1 = 0 if (x>=0) else dabSizeX-adj_x2
	bx2 = bx1+dabSizeX if (x+dabSizeX<canvSize) else canvSize - adj_x1
	by1 = 0 if (y>=0) else dabSizeY-adj_y2
	by2 = by1+dabSizeY if (y+dabSizeY<canvSize) else canvSize - adj_y1
	
	#Color the brush, slice it if is on the canvas border, and apply the brush texture on it
	source = source[by1:by2, bx1:bx2,:]
	source[:,:,3] *= brushMask[adj_y1:adj_y2, adj_x1:adj_x2]
	
	#Apply source image over destination using the SRC alpha ADD DEST inverse_alpha blending method
	inverseSource = N.subtract(1, source[:,:,3])
	normalSource = source[:,:,3]
	layerData[adj_y1:adj_y2, adj_x1:adj_x2, 0] = (((destination[:,:,0] * inverseSource) + (source[:,:,0] * normalSource))*255).astype(N.uint8)
	layerData[adj_y1:adj_y2, adj_x1:adj_x2, 1] = (((destination[:,:,1] * inverseSource) + (source[:,:,1] * normalSource))*255).astype(N.uint8)
	layerData[adj_y1:adj_y2, adj_x1:adj_x2, 2] = (((destination[:,:,2] * inverseSource) + (source[:,:,2] * normalSource))*255).astype(N.uint8)
	layerData[adj_y1:adj_y2, adj_x1:adj_x2, 3] = ((destination[:,:,3] + (1 - destination[:,:,3]) * normalSource)*255).astype(N.uint8)


#Jitted version of applyMirroredDab
@jit(void(int64, uint8[:,:,:], int64, int64, float32[:,:,:], int64, float32[:,:]), nopython=True, cache=True)
def applyMirroredDab_jit(mirror, layerData, x, y, source, canvSize, brushMask):
	#Apply the first normal dab
	applyDab_jit(layerData, x, y, source, canvSize, brushMask)

	#Mirrored horizontally
	if mirror==1 or mirror==3:
		brushSourceFlipped = N.copy(source)[:,::-1]
		applyDab_jit(layerData, layerData.shape[0]-x-brushSourceFlipped.shape[0], y, brushSourceFlipped, canvSize, brushMask)

	#Mirrored vertically
	if mirror==2 or mirror==3:
		brushSourceFlipped = N.copy(source)[::-1]
		applyDab_jit(layerData, x, layerData.shape[1]-y-source.shape[1], source, canvSize, brushMask)
	
	#Double mirrored
	if mirror==3:
		brushSourceFlipped = N.copy(source)[:,::-1]
		brushSourceFlippedFlipped = N.copy(brushSourceFlipped)[::-1]
		applyDab_jit(layerData, layerData.shape[0]-x-brushSourceFlippedFlipped.shape[0], layerData.shape[1]-y-brushSourceFlippedFlipped.shape[1], brushSourceFlippedFlipped, canvSize, brushMask)










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










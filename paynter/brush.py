#External modules
import PIL.Image
import numpy as N


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

	#Create the brush
	def __init__(self, tipImage, maskImage, size = 50, 
				angle = 0, spacing = 1, 
				fuzzyDabAngle = 0, fuzzyDabSize = 0, fuzzyDabHue = 0, fuzzyDabSat = 0, fuzzyDabVal = 0, fuzzyDabMix = 0,
				fuzzyDabScatter = 0):
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

		#Set the brush mask
		if maskImage!="":
			res = PIL.Image.open(config.ROOT+'/res/'+maskImage)
			alpha = res.split()[0] #Take only the red channel since is black and white
			bm = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE), dtype=N.float32)
			for j in range(0, config.CANVAS_SIZE, res.width):
				for i in range(0, config.CANVAS_SIZE, res.width):
					bm[i:i+res.width, j:j+res.width] = N.divide(N.array(alpha), 255)*5
			self.brushMask = 1-bm
		
		else:
			#Add default mask
			bm = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE), dtype=N.float32)
			bm[:,:] = 0
			self.brushMask = 1-bm


	def resizeBrush(self, newSize):
		if newSize==0:
			newSize = self.originalSize

		if self.realCurrentSize == newSize:
			return

		print('resizing from :'+str(self.realCurrentSize)+' to:'+str(newSize))
		self.realCurrentSize = newSize

		#Downsample the size-related parameters
		newSize = int(newSize/config.DOWNSAMPLING)

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

			

	def prepareDab(self, x, y, color, secondColor):
		#Apply scattering if any
		if self.fuzzyDabScatter != 0:
			randomAngle = randInt(0,360)
			randomLength = fuzzy(self.fuzzyDabScatter)
			x += dcos(randomAngle)*randomLength
			y += dsin(randomAngle)*randomLength

		#Round up all the coordinates and convert them to int 
		x, y = int(x-self.brushSize*0.5), int(y-self.brushSize*0.5)

		#Get the brush image image 
		brushSource = 0
		if self.multibrush:
			brushSource = self.brushTip[randInt(0,len(self.brushTip)-1)]
		else:
			brushSource = self.brushTip

		#Apply transformations
		if self.fuzzyDabAngle!=0 or self.fuzzyDabSize!=0:
			#Convert the brush to an image to ease out the rotation and resizing process
			img = PIL.Image.fromarray((brushSource*255).astype(N.uint8), 'RGBA')
			
			#Apply fuzzy scale
			if self.fuzzyDabAngle!=0:
				img = img.rotate(fuzzy(self.fuzzyDabAngle), expand=1, resample=rotateResample)
				brushSource = N.array(img)/255

			#Apply fuzzy scale
			if self.fuzzyDabSize!=0:
				fuz = fuzzy(self.fuzzyDabSize)
				img = img.resize((int(img.width*fuz), int(img.height*fuz)), resample=resizeResample)
			
			#Reconvert brushSource to an array
			brushSource = N.array(img)/255

		#Apply fuzzy color transformations
		dabColor = color.copy()
		if self.fuzzyDabHue!=0 or self.fuzzyDabSat!=0 or self.fuzzyDabVal!=0 or self.fuzzyDabMix!=0:
			#Mix colors
			if self.fuzzyDabMix!=0:
				fuz = fuzzy(self.fuzzyDabMix)
				dabColor.r = min(1, (dabColor.r*(1-fuz) + secondColor.r*fuz))
				dabColor.g = min(1, (dabColor.g*(1-fuz) + secondColor.g*fuz))
				dabColor.b = min(1, (dabColor.b*(1-fuz) + secondColor.b*fuz))
				
			#Fuzzy Hue
			if self.fuzzyDabHue!=0:
				dabColor.tweak_Hue(fuzzy(self.fuzzyDabHue))
			#Fuzzy Saturation
			if self.fuzzyDabSat!=0:
				dabColor.tweak_Sat(fuzzy(self.fuzzyDabSat))
			#Fuzzy Value
			if self.fuzzyDabVal!=0:
				dabColor.tweak_Val(fuzzy(self.fuzzyDabVal))

		#Color the brush
		coloredBrushSource = brushSource[:,:] * dabColor.get_0_1()
		
		#Return the processed dab
		return {
			'x' : x,
			'y' : y,
			'coloredBrushSource' : coloredBrushSource
		}

	#Stamp the processed dab onto the canvas
	def applyDab(self, layer, x, y, source):

		startingTime = time.time()
		
		#Extract layerdata
		layerData = layer.data

		#Get the final dab size
		dabSizeX, dabSizeY = source.shape[:2]
		
		#Adjust coordinates and make sure we are inside (at least partially) the canvas
		adj_x1, adj_y1 = clamp(x,          0, config.CANVAS_SIZE), clamp(y,          0, config.CANVAS_SIZE)
		adj_x2, adj_y2 = clamp(x+dabSizeX, 0, config.CANVAS_SIZE), clamp(y+dabSizeY, 0, config.CANVAS_SIZE)
		if adj_x1==adj_x2 or adj_y1==adj_y2:return
		
		#Get the slice and uniform to [0-1]
		destination = N.divide(N.copy(layerData[adj_y1:adj_y2, adj_x1:adj_x2].astype(N.float32)), 255)
		
		#Calculate the correct range to make sure it works even on canvas border 
		bx1 = 0 if (x>=0) else dabSizeX-adj_x2
		bx2 = bx1+dabSizeX if (x+dabSizeX<config.CANVAS_SIZE) else config.CANVAS_SIZE - adj_x1
		by1 = 0 if (y>=0) else dabSizeY-adj_y2
		by2 = by1+dabSizeY if (y+dabSizeY<config.CANVAS_SIZE) else config.CANVAS_SIZE - adj_y1
		
		#Color the brush, slice it if is on the canvas border, and apply the brush texture on it
		source = source[by1:by2, bx1:bx2, :]
		source[:, :, 3] *= self.brushMask[adj_y1:adj_y2, adj_x1:adj_x2]
		
		#Apply source image over destination using the SRC alpha ADD DEST inverse_alpha blending method
		inverseSource = 1-source[:,:,3]
		normalSource = source[:,:,3]

		layerData[adj_y1:adj_y2, adj_x1:adj_x2, 0] = ((destination[:,:,0] * (inverseSource)) + (source[:,:,0] * normalSource))*255
		print('Time8: '+str(time.time()-startingTime))

		layerData[adj_y1:adj_y2, adj_x1:adj_x2, 1] = ((destination[:,:,1] * (inverseSource)) + (source[:,:,1] * normalSource))*255
		print('Time9: '+str(time.time()-startingTime))

		layerData[adj_y1:adj_y2, adj_x1:adj_x2, 2] = ((destination[:,:,2] * (inverseSource)) + (source[:,:,2] * normalSource))*255			
		print('Time10: '+str(time.time()-startingTime))

		layerData[adj_y1:adj_y2, adj_x1:adj_x2, 3] = (destination[:,:,3] + (1 - destination[:,:,3]) * normalSource)*255;
		print('Time11: '+str(time.time()-startingTime))
		print('-------')
		
	#Make a single dab on the canvas
	def makeDab(self, layer, x, y, color, secondColor, mirror=''):
		#Prepare the dab with all the fuzzy parameters 
		dabProperties = self.prepareDab(x, y, color, secondColor)		
		x = dabProperties['x']
		y = dabProperties['y']
		coloredBrushSource = dabProperties['coloredBrushSource']

		#Apply the preprocessed dab onto the canvas with mirrors
		self.applyDab(layer, x, y, coloredBrushSource)
		if mirror=='h' or mirror=='hv':
			brushSourceFlipped = N.fliplr(N.copy(coloredBrushSource))
			self.applyDab(layer, layer.data.shape[0]-x-brushSourceFlipped.shape[0], y, brushSourceFlipped)
		if mirror=='v' or mirror=='hv':
			brushSourceFlipped = N.flipud(N.copy(coloredBrushSource))
			self.applyDab(layer, x, layer.data.shape[1]-y-coloredBrushSource.shape[1], brushSourceFlipped)
		if mirror=='hv':
			brushSourceFlipped = N.fliplr(N.copy(coloredBrushSource))
			brushSourceFlippedFlipped = N.flipud(N.copy(brushSourceFlipped))
			self.applyDab(layer, layer.data.shape[0]-x-brushSourceFlippedFlipped.shape[0], layer.data.shape[1]-y-brushSourceFlippedFlipped.shape[1], brushSourceFlippedFlipped)


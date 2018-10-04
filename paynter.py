import numpy as N
from PIL import Image
import PIL.ImageOps
import random
import math

import config

'''
TODO:
-Add randomization parameters for waterolours
-reimplement rotation on the dab step


'''



######################################################################
# Useful Functions
######################################################################

#Clamp shortcut
def clamp(x, mi, ma):
	return max(mi, min(ma, x))

#Random shortcut
def rand(a,b):
	return random.randint(a,b) #inclusive

#Degree cosine shortcut
def dcos(deg):
	return math.cos(math.radians(deg))

#Degree sine shortcut
def dsin(deg):
	return math.sin(math.radians(deg))

#Get fuzzy
def fuzzy(fuzzyRange):
	return rand(fuzzyRange[0], fuzzyRange[1])

#Image to brushtip function
def loadBrushTip(path, size, angle):
	#Open the image and make sure its RGB
	res = Image.open(path).convert('RGB')
	
	#Resize it to the target size
	factor = (size/res.width)
	resScaled = res.resize((int(res.width * factor), int(res.height * factor)))
	
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
	return bt


######################################################################
# Main classes
######################################################################
#The paynter class is the object that draw stuff on a layer using a brush and a color
class Paynter:
	brush = 0
	layer = 0
	color = [0,0,0,0]

	def drawLine(self, x1, y1, x2, y2):
		#Calculate the direction and the length of the step
		direction = math.degrees(math.atan2(y2 - y1, x2 - x1))
		length = self.brush.spacing

		#Prepare the loop
		x, y = x1, y1
		currentDist = math.sqrt((x2 - x)**2 + (y2 - y)**2)
		previousDist = currentDist+1
		
		#Do all the steps until I passed the target point
		while(previousDist>currentDist):
			#Make the dab on this point
			self.brush.makeDab(self.layer, int(x), int(y), self.color)

			#Mode the point for the next step and update the distances
			x += length*dcos(direction)
			y += length*dsin(direction)
			previousDist = currentDist
			currentDist = math.sqrt((x2 - x)**2 + (y2 - y)**2)
			
	#Setter for color, takes 0-255 RGBA
	def setColor(self, r, g, b, a=255):
		self.color = N.divide([r, g, b, a], 255)

	#Setter for layer reference
	def setLayer(self, array):
		self.layer = array

	#Setter for brush reference
	def setBrush(self, b):
		self.brush = b


#The brush class is the one that define how the current brush should behave
class Brush:
	brushTip = 0
	brushMask = 0
	brushSize = 0
	multibrush = False
	spacing = 0
	fuzzyDabAngle = 0
	fuzzyDabSize = 0

	def __init__(self, tipImage, maskImage, size = 50, 
				color = [0,0,0,0], angle = 0, spacing = 1, fuzzyDabAngle = 0, fuzzyDabSize = 0):
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
		self.fuzzyDabAngle = fuzzyDabAngle
		self.fuzzyDabSize = fuzzyDabSize

		#Set the brush mask
		if maskImage!="":
			res = Image.open(maskImage)
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
			



	def makeDab(self, layer, x, y, color):
		#brushTip = RGBA float32
		#


		#Get the brush image image 
		brushSource = 0
		if self.multibrush:
			brushSource = self.brushTip[rand(0,len(self.brushTip)-1)]
		else:
			brushSource = self.brushTip

		#Apply fuzzy angle
		#if self.fuzzyDabSize!=0:
		#	img = Image.fromarray(brushSource, 'RGBA')
		#	img = img.rotate(fuzzy(self.fuzzyDabSize), expand = 1)
		#	brushSource = N.array(img)

		#Apply fuzzy scale
		if self.fuzzyDabSize!=0:
			adaptedArray = brushSource*255
			img = Image.fromarray(adaptedArray.astype(N.uint8), 'RGBA')
			fuz = fuzzy(self.fuzzyDabSize)
			img = img.resize((int(img.width*fuz), int(img.height*fuz)))
			grayscaleValue = img.split()[0]
			brushSource = N.zeros((img.width, img.height, 4), dtype=N.float32)
			brushSource[:,:,0] = 1
			brushSource[:,:,1] = 1
			brushSource[:,:,2] = 1		
			brushSource[:,:,3] = N.divide(N.array(grayscaleValue), 255)

		#Get the final dab size
		dabSizeX = brushSource.shape[0]
		dabSizeY = brushSource.shape[1]

		#Adjust coordinates and make sure we are inside (at least partially) the canvas
		adj_x1, adj_y1 = clamp(x, 0, config.CANVAS_SIZE), clamp(y, 0, config.CANVAS_SIZE)
		adj_x2, adj_y2 = clamp(x+dabSizeX, 0, config.CANVAS_SIZE), clamp(y+dabSizeY, 0, config.CANVAS_SIZE)
		if adj_x1==adj_x2 or adj_y1==adj_y2:
			return

		#Get the slice and uniform to [0-1]
		destination = layer[adj_y1:adj_y2, adj_x1:adj_x2].astype(N.float32)
		destination /= 255

		#Calculate the correct range to make sure it works even on canvas border 
		bx1 = max(0, dabSizeX - adj_x2)
		bx2 = min(dabSizeX, config.CANVAS_SIZE - adj_x1)
		by1 = max(0, dabSizeY - adj_y2)
		by2 = min(dabSizeY, config.CANVAS_SIZE - adj_y1)

		#Color the brush, slice it if is on the canvas border, and apply the brush texture on it
		source = brushSource[:,:] * color
		source = source[by1:by2, bx1:bx2, :]
		print('source:'+str(source[:, :, 3].shape))
		print('mask:'+str(self.brushMask[adj_y1:adj_y2, adj_x1:adj_x2].shape))
		source[:, :, 3] *= self.brushMask[adj_y1:adj_y2, adj_x1:adj_x2]




		#Apply source image over destination using the SRC alpha ADD DEST inverse_alpha blending method
		final = N.zeros((adj_y2-adj_y1, adj_x2-adj_x1, 4), dtype=N.float32)
		final[:,:,0] = ((destination[:,:,0] * (1-source[:,:,3])) + (source[:,:,0] * (source[:,:,3])))*255
		final[:,:,1] = ((destination[:,:,1] * (1-source[:,:,3])) + (source[:,:,1] * (source[:,:,3])))*255
		final[:,:,2] = ((destination[:,:,2] * (1-source[:,:,3])) + (source[:,:,2] * (source[:,:,3])))*255		
		final[:,:,3] = ((destination[:,:,3] * (1-source[:,:,3])) + (source[:,:,3] * (source[:,:,3])))*255
		layer[adj_y1:adj_y2, adj_x1:adj_x2] = final.astype(N.uint8)












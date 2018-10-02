import numpy as N
from PIL import Image
import PIL.ImageOps
import random
import math

'''
TODO:
-Do a proper wrapping around brush textures
-Add spacing to brushes
-Add randomization parameters for waterolours
-reimplement rotation on the dab step
-Check for dab outside the layer


'''



######################################################################
# Useful Functions
######################################################################

#Random shortcut
def rand(a,b):
	return random.randint(a,b) #inclusive

#Degree cosine shortcut
def dcos(deg):
	return math.cos(math.radians(deg))

#Degree sine shortcut
def dsin(deg):
	return math.sin(math.radians(deg))

#Image to brushtip function
def loadBrushTip(path, size):
	#Open the image and make sure its RGB
	res = Image.open(path).convert('RGB')
	
	#Resize it to the target size
	factor = (size/res.width)
	resScaled = res.resize((int(res.width * factor), int(res.height * factor)))
	
	#Invert and grab the value
	resScaled = PIL.ImageOps.invert(resScaled)
	grayscaleValue = resScaled.split()[0]

	#Create the brushtip image
	bt = N.zeros((size,size, 4), dtype=N.float32)
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
		direction = math.atan2(y2 - y1, x2 - x1)
		print('direction:'+str(direction))
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
			print(currentDist)
			
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
	maskSize = 0
	multibrush = False
	spacing = 0

	def __init__(self, tipImage, maskImage, size = 50, 
				color = [0,0,0,0], angle = 0, spacing = 1):
		#Set the brushTip
		if isinstance(tipImage, list):
			#Multibrush
			self.brushTip = []
			for image in tipImage:
				bt = loadBrushTip(image, size)
				self.brushTip.append(bt)
			self.multibrush = True
		else:
			#NormalBrush
			self.brushTip = loadBrushTip(tipImage, size)
		
		#Set the perameters
		self.brushSize = size
		self.spacing = size*spacing

		#Set the brush mask
		self.maskSize = 2048
		if maskImage!="":
			res = Image.open(maskImage)
			factor = (self.maskSize/res.width)
			resScaled = res.resize((int(res.width * factor), int(res.height * factor)))
			alpha = resScaled.split()[0] #Take only the red channel since is black and white
			bm = N.zeros((self.maskSize,self.maskSize), dtype=N.float32)
			bm[:,:] = N.divide(N.array(alpha), 255)*5
			self.brushMask = 1-bm
		else:
			#Add default mask
			bm = N.zeros((self.maskSize,self.maskSize), dtype=N.float32)
			bm[:,:] = 0
			self.brushMask = 1-bm
			



	def makeDab(self, layer, x, y, color):
		#Get the slice and uniform to [0-1]
		destination = layer[y:y+self.brushSize, x:x+self.brushSize].astype(N.float32)
		destination /= 255

		#Calculate Source image 
		brushSource = 0
		if self.multibrush:
			brushSource = self.brushTip[rand(0,len(self.brushTip)-1)]
		else:
			brushSource = self.brushTip
		source = brushSource[:,:] * color
		source[:,:,3] *= self.brushMask[y:y+self.brushSize, x:x+self.brushSize]
		
		#Apply source image over destination using the SRC alpha ADD DEST inverse_alpha blending method
		final = N.zeros((self.brushSize,self.brushSize, 4), dtype=N.float32)
		final[:,:,0] = ((destination[:,:,0] * (1-source[:,:,3])) + (source[:,:,0] * (source[:,:,3])))*255
		final[:,:,1] = ((destination[:,:,1] * (1-source[:,:,3])) + (source[:,:,1] * (source[:,:,3])))*255
		final[:,:,2] = ((destination[:,:,2] * (1-source[:,:,3])) + (source[:,:,2] * (source[:,:,3])))*255		
		final[:,:,3] = ((destination[:,:,3] * (1-source[:,:,3])) + (source[:,:,3] * (source[:,:,3])))*255
		layer[y:y+self.brushSize,x:x+self.brushSize] = final.astype(N.uint8)












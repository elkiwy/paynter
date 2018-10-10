import numpy as N
import PIL.Image
import PIL.ImageOps
import random
import math
import colorsys

import config

'''
TODO:
-add mirror fuzzy 
-add flood fill
-Add proper layer effects managing



'''

resizeResample = PIL.Image.LANCZOS
rotateResample = PIL.Image.NEAREST


######################################################################
# Useful Functions
######################################################################

#Take 0-1 hsv and outputs a 0-1 rgb
def hsv2rgb(hsv):
    return N.asarray(colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))

#Take 0-1 rgb and outputs 0-1 hsv
def rgb2hsv(rgb):
    return N.asarray(colorsys.rgb_to_hsv(rgb[0],rgb[1],rgb[2]))

#Clamp shortcut
def clamp(x, mi, ma):
	return max(mi, min(ma, x))

#Random shortcut
def randInt(a,b):
	return random.randint(a,b) #inclusive

#Random shortcut
def randFloat(a,b):
	return random.uniform(a,b)

#Degree cosine shortcut
def dcos(deg):
	return math.cos(math.radians(deg))

#Degree sine shortcut
def dsin(deg):
	return math.sin(math.radians(deg))

#Get fuzzy
def fuzzy(fuzzyRange):
	return randFloat(fuzzyRange[0], fuzzyRange[1])

#Image to brushtip function
def loadBrushTip(path, size, angle):
	#Open the image and make sure its RGB
	res = PIL.Image.open(path).convert('RGB')
	
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


######################################################################
# Color Management functions
######################################################################
#Get 3 colors with a triad pattern
def getColors_Triad(sat = 1, val = 1, spread = 60):
	palette = list()
	leadHue = randFloat(0, 1)

	#First color
	hsv = [	leadHue, sat, val]
	rgb = hsv2rgb(hsv)*255
	rgba = [rgb[0], rgb[1], rgb[2], 255]
	palette.append(rgba)

	#Second color
	hsv = [	(leadHue + 0.5 + spread/360) % 1, sat, val]
	rgb = hsv2rgb(hsv)*255
	rgba = [rgb[0], rgb[1], rgb[2], 255]
	palette.append(rgba)

	#Third
	hsv = [	(leadHue + 0.5 - spread/360) % 1, sat, val]
	rgb = hsv2rgb(hsv)*255
	rgba = [rgb[0], rgb[1], rgb[2], 255]
	palette.append(rgba)

	return palette 

#Change the hue of a color
def tweakColorHue(rgba, ammount):
	hsv = rgb2hsv(N.asarray(rgba[:3])/255)
	hsv[0] = (hsv[0] + ammount) % 1
	rgba[:3] = hsv2rgb(hsv)
	rgba[0] *= 255
	rgba[1] *= 255
	rgba[2] *= 255
	return rgba

#Change the saturation of a color
def tweakColorSat(rgba, ammount):
	hsv = rgb2hsv(N.asarray(rgba[:3])/255)
	hsv[1] = clamp(hsv[1] + ammount, 0, 1)
	rgba[:3] = hsv2rgb(hsv)
	rgba[0] *= 255
	rgba[1] *= 255
	rgba[2] *= 255
	return rgba

#Change the value of a color
def tweakColorVal(rgba, ammount):
	print(rgba)
	hsv = rgb2hsv(N.asarray(rgba[:3])/255)
	hsv[2] = clamp(hsv[2] + ammount, 0, 1)
	rgba[:3] = hsv2rgb(hsv)
	rgba[0] *= 255
	rgba[1] *= 255
	rgba[2] *= 255
	return rgba



######################################################################
# Layer Functions
######################################################################
#The layer class the the one holding all the data and effecct to show how to add colors when merging layers
class Layer:
	effect = ''
	data = 0

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

	def showLayer(self, title=''):
		PIL.Image.fromarray(self.data, 'RGBA').show(title=title)


def lighten(img_in, img_layer, opacity):
	img_in /= 255.0
	img_layer /= 255.0

	print(img_in)
	comp_alpha = N.minimum(img_in[:, :, 3], img_layer[:, :, 3])*opacity
	new_alpha = img_in[:, :, 3] + (1.0 - img_in[:, :, 3])*comp_alpha
	ratio = comp_alpha/new_alpha
	ratio[ratio == N.NAN] = 0.0

	print(ratio)

	comp = N.maximum(img_in[:, :, :3], img_layer[:, :, :3])
	ratio_rs = N.reshape(N.repeat(ratio, 3), [comp.shape[0], comp.shape[1], comp.shape[2]])
	img_out = comp*ratio_rs + img_in[:, :, :3] * (1.0-ratio_rs)
	img_out = N.nan_to_num(N.dstack((img_out, img_in[:, :, 3])))  # add alpha channel and replace nans
	
	print(img_out)
	return img_out*255.0


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

	def mergeAllLayers(self):
		while(len(self.layers)>1):
			self.mergeBottomLayers()
		return self.layers[0]

	def mergeBottomLayers(self):
		print('merging top layers')
		if self.layers[1].effect=='lighten':
			baseImage = self.layers[0].data.astype(N.float32)
			overImage = self.layers[1].data.astype(N.float32)
			newImage = lighten(baseImage, overImage, 1).astype(N.uint8)
			#self.layers.pop()
			#self.layers.pop()
			del self.layers[0]
			#del self.layers[0]
			finalLayer = Layer(data = newImage)
			finalLayer.showLayer('test')
			self.layers[0] = finalLayer


		else:
			baseImage = PIL.Image.fromarray(self.layers[0].data, 'RGBA')
			overImage = PIL.Image.fromarray(self.layers[1].data, 'RGBA')
			baseImage.paste(overImage, (0, 0), overImage)
			del self.layers[0]
			#del self.layers[0]
			self.layers[0] = Layer(data = N.array(baseImage))
			#self.layers.append(Layer(data = N.array(baseImage)))

		self.layers[0].showLayer()
			




######################################################################
# Paynter class
######################################################################
#The paynter class is the object that draw stuff on a layer using a brush and a color
class Paynter:
	brush = 0
	layer = 0
	color = [0, 0, 0, 1]
	secondColor = [1, 1, 1, 1]
	image = 0

	#Init the paynter
	def __init__(self):
		#Setup some stuff
		config.CANVAS_SIZE = int(config.REAL_CANVAS_SIZE/config.DOWNSAMPLING)
		self.image = Image()

	#Draw a line between two points
	def drawLine(self, x1, y1, x2, y2):
		#Downsample the coordinates
		x1 = int(x1/config.DOWNSAMPLING)
		x2 = int(x2/config.DOWNSAMPLING)
		y1 = int(y1/config.DOWNSAMPLING)
		y2 = int(y2/config.DOWNSAMPLING)
		print('drawing line from: '+str((x1,y1))+' to: '+str((x2,y2)))

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
			self.brush.makeDab(self.image.getActiveLayer(), int(x), int(y), self.color, self.secondColor)

			#Mode the point for the next step and update the distances
			x += length*dcos(direction)
			y += length*dsin(direction)
			previousDist = currentDist
			currentDist = math.sqrt((x2 - x)**2 + (y2 - y)**2)

	#Draw a single dab
	def drawPoint(self, x, y):
		x = int(x/config.DOWNSAMPLING)
		y = int(y/config.DOWNSAMPLING)
		self.brush.makeDab(self.image.getActiveLayer(), int(x), int(y), self.color, self.secondColor)

	#Fill the current layer with a color
	def fillLayerWithColor(self, color):
		layer = self.image.getActiveLayer().data
		layer[:,:,0] = color[0]
		layer[:,:,1] = color[1]
		layer[:,:,2] = color[2]

	#Setter for color, takes 0-255 RGBA
	def setColor(self, r=0, g=0, b=0, a=255):
		#Separated paramters
		if isinstance(r, int):
			self.color = N.divide([r, g, b, a], 255)
		#RGBA list 
		else:
			self.color = N.divide([r[0], r[1], r[2], r[3]], 255)

	#Swap between first and second color
	def swapColors(self):
		temp = N.copy(self.color)
		self.color = self.secondColor
		self.secondColor = temp

	#Setter for brush reference
	def setBrush(self, b):
		self.brush = b


	def renderImage(self):
		#Make sure the alpha on the base layer is ok
		self.image.layers[0].data[:,:,3] = 255

		#for layer in self.image.layers:
		#	layer.showLayer()


		resultLayerData = self.image.mergeAllLayers().data


		#Show the results
		img = PIL.Image.fromarray(resultLayerData, 'RGBA')
		img.show()


######################################################################
# Brush class
######################################################################

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

	#Create the brush
	def __init__(self, tipImage, maskImage, size = 50, 
				color = [0,0,0,0], angle = 0, spacing = 1, 
				fuzzyDabAngle = 0, fuzzyDabSize = 0, fuzzyDabHue = 0, fuzzyDabSat = 0, fuzzyDabVal = 0, fuzzyDabMix = 0,
				fuzzyDabScatter = 0):
		#Downsample the size-related parameters
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
		self.fuzzyDabAngle = fuzzyDabAngle
		self.fuzzyDabSize = fuzzyDabSize
		self.fuzzyDabHue = fuzzyDabHue
		self.fuzzyDabSat = fuzzyDabSat
		self.fuzzyDabVal = fuzzyDabVal
		self.fuzzyDabMix = fuzzyDabMix
		self.fuzzyDabScatter = fuzzyDabScatter

		#Set the brush mask
		if maskImage!="":
			res = PIL.Image.open(maskImage)
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
			


	#Make a single dab on the canvas
	def makeDab(self, layer, x, y, color, secondColor):
		#Extract the layerData
		layer = layer.data

		#Apply scattering if any
		if self.fuzzyDabScatter != 0:
			randomAngle = randInt(0,360)
			randomLength = fuzzy(self.fuzzyDabScatter)
			x += dcos(randomAngle)*randomLength
			y += dsin(randomAngle)*randomLength

		#Round up all the coordinates and convert them to int 
		x = int(round(x))
		y = int(round(y))
		if config.DEBUG:
			print('-----------------------------')
			print('make dab: '+str(x)+','+str(y) +' color :' +str(color))
			print('layer: '+str(layer.shape))

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
		dabColor = N.copy(color)
		if self.fuzzyDabHue!=0 or self.fuzzyDabSat!=0 or self.fuzzyDabVal!=0 or self.fuzzyDabMix!=0:
			#Mix colors
			if self.fuzzyDabMix!=0:
				fuz = fuzzy(self.fuzzyDabMix)
				dabColor[0] = min(1, (dabColor[0]*(1-fuz) + secondColor[0]*fuz))
				dabColor[1] = min(1, (dabColor[1]*(1-fuz) + secondColor[1]*fuz))
				dabColor[2] = min(1, (dabColor[2]*(1-fuz) + secondColor[2]*fuz))
				
			#Convert to hsv
			hsv = rgb2hsv(dabColor[:3])

			#Fuzzy Hue
			if self.fuzzyDabHue!=0:
				hsv[0] = (hsv[0] + fuzzy(self.fuzzyDabHue)) % 1
			#Fuzzy Saturation
			if self.fuzzyDabSat!=0:
				hsv[1] = clamp(hsv[1] + fuzzy(self.fuzzyDabSat), 0, 1)
			#Fuzzy Value
			if self.fuzzyDabVal!=0:
				hsv[2] = clamp(hsv[2] + fuzzy(self.fuzzyDabVal), 0, 1)

			#Convert back to rgb
			dabColor[:3] = hsv2rgb(hsv)

		#Get the final dab size
		dabSizeX = brushSource.shape[0]
		dabSizeY = brushSource.shape[1]
		if config.DEBUG:
			print('dabSize:'+str(dabSizeX)+" ; "+str(dabSizeY)+' canvas:'+str(config.CANVAS_SIZE))

		#Adjust coordinates and make sure we are inside (at least partially) the canvas
		adj_x1, adj_y1 = clamp(x,          0, config.CANVAS_SIZE), clamp(y,          0, config.CANVAS_SIZE)
		adj_x2, adj_y2 = clamp(x+dabSizeX, 0, config.CANVAS_SIZE), clamp(y+dabSizeY, 0, config.CANVAS_SIZE)
		if adj_x1==adj_x2 or adj_y1==adj_y2:
			return

		#Get the slice and uniform to [0-1]
		destination = layer[adj_y1:adj_y2, adj_x1:adj_x2].astype(N.float32)
		destination /= 255

		#Calculate the correct range to make sure it works even on canvas border 
		bx1 = 0 if (x>=0) else dabSizeX-adj_x2
		bx2 = bx1+dabSizeX if (x+dabSizeX<config.CANVAS_SIZE) else config.CANVAS_SIZE - adj_x1
		by1 = 0 if (y>=0) else dabSizeY-adj_y2
		by2 = by1+dabSizeY if (y+dabSizeY<config.CANVAS_SIZE) else config.CANVAS_SIZE - adj_y1
		if config.DEBUG:
			print('brush/layer     ['+str(adj_y1)+":"+str(adj_y2)+','+str(adj_x1)+":"+str(adj_x2)+"]")
			print('source = source ['+str(by1)+":"+str(by2)+','+str(bx1)+":"+str(bx2)+"]")

		#Color the brush, slice it if is on the canvas border, and apply the brush texture on it
		source = brushSource[:,:] * dabColor
		source = source[by1:by2, bx1:bx2, :]
		if config.DEBUG:
			print('source shape :'+str(source.shape))
			print('desti  shape :'+str(destination.shape))
		source[:, :, 3] *= self.brushMask[adj_y1:adj_y2, adj_x1:adj_x2]

		#Apply source image over destination using the SRC alpha ADD DEST inverse_alpha blending method
		final = N.zeros((adj_y2-adj_y1, adj_x2-adj_x1, 4), dtype=N.float32)
		if config.DEBUG:
			print('final  shape :'+str(final.shape))
			print('-----------------------------')
		final[:,:,0] = ((destination[:,:,0] * (1-source[:,:,3])) + (source[:,:,0] * (source[:,:,3])))*255
		final[:,:,1] = ((destination[:,:,1] * (1-source[:,:,3])) + (source[:,:,1] * (source[:,:,3])))*255
		final[:,:,2] = ((destination[:,:,2] * (1-source[:,:,3])) + (source[:,:,2] * (source[:,:,3])))*255		
		final[:,:,3] = ((destination[:,:,3] * (1-source[:,:,3])) + (source[:,:,3] * (source[:,:,3])))*255
		layer[adj_y1:adj_y2, adj_x1:adj_x2] = final.astype(N.uint8)











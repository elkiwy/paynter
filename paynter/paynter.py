#External modules
import numpy as N
import PIL.Image
import PIL.ImageOps
import PIL.ImageFont
import PIL.ImageDraw 


#PaYnter Modules
from .blendModes import *
from .brush import *
from .utils import *
from .image import *
from .layer import *
import paynter.config as config


from numba import jit, float32
import time


'''
TODO:
-add asserts to main functions
'''

######################################################################
# Paynter class
######################################################################
#The paynter class is the object that draw stuff on a layer using a brush and a color
class Paynter:
	brush = 0
	layer = 0
	color = Color(0, 0, 0, 1)
	secondColor = Color(1,1,1,1)
	image = 0
	mirrorMode = 0

	#Init the paynter
	def __init__(self):
		#Setup some stuff
		config.CANVAS_SIZE = int(config.REAL_CANVAS_SIZE/config.DOWNSAMPLING)
		self.image = Image()



	######################################################################
	# Level 0 Functions, needs downsampling
	######################################################################
	#Draw a line between two points
	def drawLine(self, x1, y1, x2, y2):
		start = time.time()

		#Downsample the coordinates
		x1 = int(x1/config.DOWNSAMPLING)
		x2 = int(x2/config.DOWNSAMPLING)
		y1 = int(y1/config.DOWNSAMPLING)
		y2 = int(y2/config.DOWNSAMPLING)
		print('drawing line from: '+str((x1,y1))+' to: '+str((x2,y2)))

		#Calculate the direction and the length of the step
		direction = N.arctan2(y2 - y1, x2 - x1)
		length = self.brush.spacing

		#Prepare the loop
		x, y = x1, y1
		totalSteps = int(N.sqrt((x2 - x)**2 + (y2 - y)**2)/length)
		lay = self.image.getActiveLayer()
		col = self.color
		secCol = self.secondColor
		mirr = self.mirrorMode

		#If I use source caching..
		if self.brush.usesSourceCaching:
			#..than optimize it for faster drawing
			laydata = lay.data
			x -= self.brush.brushSize*0.5
			y -= self.brush.brushSize*0.5
			colbrsource = self.brush.coloredBrushSource
			canvSize = config.CANVAS_SIZE
			brmask = self.brush.brushMask
			for _ in range(totalSteps):
				#Make the dab on this point
				applyMirroredDab_jit(mirr, laydata, int(x), int(y), colbrsource.copy(), canvSize, brmask)

				#Mode the point for the next step and update the distances
				x += lendir_x(length, direction)
				y += lendir_y(length, direction)
		#..if I don't use source caching..
		else:
			#..do the normal drawing
			for _ in range(totalSteps):
				#Make the dab on this point
				self.brush.makeDab(lay, int(x), int(y), col, secCol, mirror=mirr)

				#Mode the point for the next step and update the distances
				x += lendir_x(length, direction)
				y += lendir_y(length, direction)
			
		
	#Draw a single dab
	def drawPoint(self, x, y):
		start = time.time()

		#Downsample the coordinates
		x = int(x/config.DOWNSAMPLING)
		y = int(y/config.DOWNSAMPLING)

		#Apply the dab with or without source caching
		if self.brush.usesSourceCaching:
			applyMirroredDab_jit(self.mirrorMode, self.image.getActiveLayer().data, int(x-self.brush.brushSize*0.5), int(y-self.brush.brushSize*0.5), self.brush.coloredBrushSource.copy(), config.CANVAS_SIZE, self.brush.brushMask)
		else:
			self.brush.makeDab(self.image.getActiveLayer(), int(x), int(y), self.color, self.secondColor, mirror=self.mirrorMode)
		config.AVGTIME.append(time.time()-start)
		
	######################################################################
	# Level 1 Functions, calls Level 0 functions, no downsampling
	######################################################################
	#Draw a path from a series of points
	def drawPath(self, pointList):
		self.drawLine(pointList[0][0], pointList[0][1], pointList[1][0], pointList[1][1])
		i = 1
		while i<len(pointList)-1:
			self.drawLine(pointList[i][0], pointList[i][1], pointList[i+1][0], pointList[i+1][1])
			i+=1

	#Draw a path from a series of points
	def drawClosedPath(self, pointList):
		self.drawLine(pointList[0][0], pointList[0][1], pointList[1][0], pointList[1][1])
		i = 1
		while i<len(pointList)-1:
			self.drawLine(pointList[i][0], pointList[i][1], pointList[i+1][0], pointList[i+1][1])
			i+=1
		self.drawLine(pointList[-1][0], pointList[-1][1], pointList[0][0], pointList[0][1])
		
	#Draw a rectangle
	def drawRect(self, x1, y1, x2, y2, angle=0):
		vertices = [[x1,y1],[x2,y1],[x2,y2],[x1,y2],]
		rotatedVertices = rotateMatrix(vertices, (x1+x2)*0.5, (y1+y2)*0.5, angle)
		self.drawClosedPath(rotatedVertices)

	#Fill the current layer with a color
	def fillLayerWithColor(self, color):
		layer = self.image.getActiveLayer().data
		colorRGBA = color.get_0_255()
		layer[:,:,0] = colorRGBA[0]
		layer[:,:,1] = colorRGBA[1]
		layer[:,:,2] = colorRGBA[2]
		layer[:,:,3] = colorRGBA[3]

	#Add border to image
	def addBorder(self, width, color=None):
		width = int(width/config.DOWNSAMPLING)
		if color==None:
			color = self.color
		layer = self.image.getActiveLayer().data
		colorRGBA = color.get_0_255()
		print('adding border'+str(colorRGBA)+str(width)+str(layer.shape))
		layer[0:width,:,0] = colorRGBA[0]
		layer[0:width,:,1] = colorRGBA[1]
		layer[0:width,:,2] = colorRGBA[2]
		layer[0:width,:,3] = colorRGBA[3]

		layer[:,0:width,0] = colorRGBA[0]
		layer[:,0:width,1] = colorRGBA[1]
		layer[:,0:width,2] = colorRGBA[2]
		layer[:,0:width,3] = colorRGBA[3]

		layer[layer.shape[0]-width:layer.shape[0],:,0] = colorRGBA[0]
		layer[layer.shape[0]-width:layer.shape[0],:,1] = colorRGBA[1]
		layer[layer.shape[0]-width:layer.shape[0],:,2] = colorRGBA[2]
		layer[layer.shape[0]-width:layer.shape[0],:,3] = colorRGBA[3]

		layer[:,layer.shape[1]-width:layer.shape[1],0] = colorRGBA[0]
		layer[:,layer.shape[1]-width:layer.shape[1],1] = colorRGBA[1]
		layer[:,layer.shape[1]-width:layer.shape[1],2] = colorRGBA[2]
		layer[:,layer.shape[1]-width:layer.shape[1],3] = colorRGBA[3]




	######################################################################
	# Setters, getters, and more
	######################################################################
	#Setter for color, takes 0-255 RGBA
	def setColor(self, color):
		self.color = color
		if self.brush and self.brush.doesUseSourceCaching():
			self.brush.cacheBrush(color)

	#Change only the alpha of the current color
	def setColorAlpha(self, fixed=None, proportional=None):
		if fixed!=None:
			self.color.set_alpha(fixed)
		elif proportional!=None:
			self.color.set_alpha(self.color.get_alpha()*proportional)

	#Gets the brush alpha
	def getColorAlpha(self):
		return self.color.get_alpha()

	#Gets the brush size
	def getBrushSize(self):
		return self.brush.brushSize

	#Swap between first and second color
	def swapColors(self):
		rgba = self.color.get_0_255()
		self.color = self.secondColor
		self.secondColor = Color(rgba, '0-255')

	#Setter for brush reference
	def setBrush(self, b, resize=0, proportional=None):
		if proportional!=None:
			resize = int(self.brush.brushSize*0.5)
		b.resizeBrush(resize) #If resize=0 it reset to its default size
		self.brush = b
		if self.brush and self.brush.doesUseSourceCaching():
			self.brush.cacheBrush(self.color)

	#Setter for the mirror mode
	def setMirrorMode(self, mirror):
		assert (mirror=='' or mirror=='h' or mirror=='v' or mirror=='hv'or mirror=='vh'), 'setMirrorMode: wrong mirror mode, got '+str(mirror)+' expected one of ["","h","v","hv"]'
		
		#Round up all the coordinates and convert them to int		
		if mirror=='': 		mirror = 0
		elif mirror=='h': 	mirror = 1
		elif mirror=='v': 	mirror = 2
		elif mirror=='hv': 	mirror = 3
		elif mirror=='vh': 	mirror = 3
		self.mirrorMode = mirror
		
	#Render the final image
	def renderImage(self, output='', show=True):
		#Merge all the layers to apply blending modes
		resultLayer = self.image.mergeAllLayers()

		#Show and save the results
		img = PIL.Image.fromarray(resultLayer.data, 'RGBA')
		
		if show:
			img.show()

		if output!='':
			img.save(output, 'PNG')

	#Shortcut for image operations
	def newLayer(self, effect=''):
		self.image.newLayer(effect)

	#Shortcut for image operations
	def setActiveLayerEffect(self, effect):
		self.image.layers[self.image.activeLayer].effect = effect

	#Shortcut for image operations
	def duplicateActiveLayer(self):
		self.image.duplicateActiveLayer()

















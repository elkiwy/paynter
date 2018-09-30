import numpy as N
from PIL import Image

class Paynter:
	brush = 0
	layer = 0
	color = [0,0,0,0]

	def drawLine(self, x1, y1, x2, y2):
		for i in N.arange(0, 1, 0.01):
			x = x1 + i*(x2-x1)
			y = y1 + i*(y2-y1)
			#self.layer[int(x), int(y)] = self.color
			self.brush.makeDab(self.layer, int(x), int(y), self.color)

	def setColor(self, r, g, b, a):
		self.color = N.divide([r, g, b, a], 255)

	def setLayer(self, array):
		self.layer = array

	def setBrush(self, b):
		self.brush = b



class Brush:
	brushTip = 0
	brushMask = 0
	#fuzzySize = [0.45, 0.55]
	brushSize = 0
	maskSize = 0

	def __init__(self, tipImage, maskImage, size=50, color=[0,0,0,0]):
		#Set the brushTip
		res = Image.open("gradient_white.png")
		factor = (size/res.width)
		resScaled = res.resize((int(res.width * factor), int(res.height * factor)))
		alpha = resScaled.split()[-1]
		
		bt = N.zeros((size,size, 4), dtype=N.float32)
		bt[:,:,0] = 1
		bt[:,:,1] = 1
		bt[:,:,2] = 1		
		bt[:,:,3] = N.divide(N.array(alpha), 255)
		self.brushTip = bt
		
		self.brushSize = size


		#Set the brush mask
		#self.maskSize = 512
		#res = Image.open("paperGrain.png")
		#factor = (self.maskSize/res.width)
		#resScaled = res.resize((int(res.width * factor), int(res.height * factor)))
		#alpha = resScaled.split()[0] #Take only the red channel since is black and white
		#bm = N.zeros((self.maskSize,self.maskSize), dtype=N.float32)
		#bm[:,:] = N.divide(N.array(alpha), 255)
		#self.brushMask = bm



	def makeDab(self, layer, x, y, color):
		#Get the slice and uniform to [0-1]
		destination = layer[y:y+self.brushSize,x:x+self.brushSize].astype(N.float32)
		destination /= 255

		#(50,50,4)  (50,50,4)     (4)
		source = N.zeros((50,50, 4), dtype=N.float32)
		source[:,:,0] = self.brushTip[:,:,0] * color[0]
		source[:,:,1] = self.brushTip[:,:,1] * color[1]
		source[:,:,2] = self.brushTip[:,:,2] * color[2]
		source[:,:,3] = self.brushTip[:,:,3] * color[3]

		#Use the SRC alpha ADD DEST inverse_alpha blending method
		final = N.zeros((50,50, 4), dtype=N.float32)
		final[:,:,0] = ((destination[:,:,0] * (1-source[:,:,3])) + (source[:,:,0] * (source[:,:,3])))*255
		final[:,:,1] = ((destination[:,:,1] * (1-source[:,:,3])) + (source[:,:,1] * (source[:,:,3])))*255
		final[:,:,2] = ((destination[:,:,2] * (1-source[:,:,3])) + (source[:,:,2] * (source[:,:,3])))*255		
		final[:,:,3] = ((destination[:,:,3] * (1-source[:,:,3])) + (source[:,:,3] * (source[:,:,3])))*255
		final = final.astype(N.uint8)
		layer[y:y+self.brushSize,x:x+self.brushSize] = final



'''
brush 		= [1, 1, 1, 0.5]
color 		= [1, 1, 1, 1]

source 		= [1, 1, 1, 0.5]


1*0.5 + 0.5*0.5
0.5 + 0.25
0.75


destination = [1, 1, 1, 1]


actual 		= []

'''














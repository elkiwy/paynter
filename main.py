#External modules
import numpy as N
from PIL import Image

#PaYnter Modules
from paynter import *
import config

#Python base libs
import time

#Start the timer for banchmarks
start = time.time()

#Setup config
config.REAL_CANVAS_SIZE = 2048
config.DEBUG = False
config.DOWNSAMPLING = 4

#Create the paynter
paynter = Paynter()
image = paynter.image

#Create a palette
palette = getColors_Triad(spread = 20)
palette[0] = tweakColorVal(palette[0], -0.9)
palette[1] = tweakColorSat(palette[1], -0.65)
palette[2] = tweakColorSat(palette[2], -0.65)

#Create the brushes
pencil = Brush( "gradient.png", "paperGrain.png", size=50, angle=45, spacing=0.02)
pixel = Brush( "pixel.png", "", size = 300, spacing = 1)
watercolor = Brush( ["watercolor1.png","watercolor2.png","watercolor3.png","watercolor4.png","watercolor5.png"], "", size=440, angle=0, spacing = 0.5, fuzzyDabAngle = [0, 360], fuzzyDabSize = [1, 2], fuzzyDabHue = [-0.03, 0.03], fuzzyDabSat = [-0.2, 0.2], fuzzyDabVal = [-0.1, 0.1], fuzzyDabMix = [0.4, 0.5], fuzzyDabScatter = [0, 300])


#paynter.fillLayerWithColor(palette[0])

#Draw things
#image.newLayer()
#paynter.setBrush(watercolor)
#paynter.setColor(palette[1])
#gap = 384
#i=-2
#paynter.drawLine(-gap,   gap*i,	config.REAL_CANVAS_SIZE+gap, gap*(i+1))
#i+=1
#while i*gap < config.REAL_CANVAS_SIZE:
#	paynter.drawLine(config.REAL_CANVAS_SIZE+gap,      gap*i,                    -gap,  gap*(i+1))
#	paynter.drawLine(                  -gap,  gap*(i+1),  config.REAL_CANVAS_SIZE+gap,  gap*(i+2))
#	i+=1
#paynter.drawLine(config.REAL_CANVAS_SIZE+gap,  0+gap*i,	-gap,   0+gap*(i+1))
#paynter.setBrush(pencil)
#paynter.setColor(255,0,0)
#paynter.drawLine(100,100,300,100)
#
#image.newLayer(effect='lighten')
##image.newLayer()
#paynter.setBrush(watercolor)
#paynter.setColor(palette[2])
#gap = 384
#i=-2
#paynter.drawLine(-gap,   gap*i,	config.REAL_CANVAS_SIZE+gap, gap*(i+1))
#i+=1
#while i*gap < config.REAL_CANVAS_SIZE:
#	paynter.drawLine(config.REAL_CANVAS_SIZE+gap,      gap*i,                    -gap,  gap*(i+1))
#	paynter.drawLine(                  -gap,  gap*(i+1),  config.REAL_CANVAS_SIZE+gap,  gap*(i+2))
#	i+=1
#paynter.drawLine(config.REAL_CANVAS_SIZE+gap,  0+gap*i,	-gap,   0+gap*(i+1))
#paynter.setBrush(pencil)
#paynter.setColor(0,255,0)
#paynter.drawLine(200,100,200,300)




image.newLayer()
paynter.setBrush(pixel)
paynter.setColor(0,255,0)
paynter.drawPoint(0,0)
paynter.drawPoint(200,0)
paynter.drawPoint(0,200)
paynter.drawPoint(200,200)


image.newLayer(effect='lighten')
paynter.setColor(255,128,0)
paynter.drawPoint(100,100)









#Print the execution time
end = time.time()
print('Execution time: '+str(end-start))

paynter.renderImage()





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
config.CANVAS_SIZE = 2048

#Create the paynter
paynter = Paynter()

#Create the brushes
pencil = Brush(
	"gradient.png",
	"paperGrain.png",
	size=50,
	angle=45,
	spacing=0.02)

watercolor = Brush(
	["watercolor1.png","watercolor2.png","watercolor3.png","watercolor4.png","watercolor5.png"],
	"",
	size=220,
	angle=0,
	spacing = 0.75,
	fuzzyDabAngle = [0, 360],
	fuzzyDabSize = [1, 2])

#Create the first layer 
data = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE, 4), dtype=N.uint8)
data[:,:,3] = 255
data[:,:256,:3] = 255

#Draw things
paynter.setLayer(data)
paynter.setBrush(pencil)
#paynter.setColor(255, 0, 0)
#paynter.drawLine( -100,  100, 3000,  100)
#paynter.drawLine(  100, -100,  100, 3000)
#paynter.drawLine( -100, -100, 3000, 3000)
#paynter.drawLine( 3000, -100, -100, 3000)
#
#paynter.setColor(255, 255, 255, 255)
#paynter.drawLine(100, 200, 900, 200)

paynter.setBrush(watercolor)
paynter.setColor(255, 0, 0, 255)
paynter.drawLine(1000, 1000, 1100, 1100)
paynter.setColor(0, 255, 0, 255)
paynter.drawLine(1000, 1000, 1100, 1100)
paynter.setColor(0, 0, 255, 255)
paynter.drawLine(1000, 1000, 1100, 1100)

#Make sure the alpha on the base layer is ok
data[:,:,3] = 255

#Print the execution time
end = time.time()
print('Execution time: '+str(end-start))

#Show the results
img = Image.fromarray(data, 'RGBA')
img.show()





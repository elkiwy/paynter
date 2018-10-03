import numpy as N
from PIL import Image

from paynter import *
import config

import time








start = time.time()



config.CANVAS_SIZE = 2048



paynter = Paynter()

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
	spacing = 0.75)

data = N.zeros((config.CANVAS_SIZE, config.CANVAS_SIZE, 4), dtype=N.uint8)
data[:,:,3] = 255
data[:,:256,:3] = 255




paynter.setLayer(data)
paynter.setBrush(pencil)
paynter.setColor(0, 0, 0, 255)
paynter.drawLine(100, 100, 900, 100)
paynter.setColor(255, 255, 255, 255)
paynter.drawLine(100, 200, 900, 200)

paynter.setBrush(watercolor)
paynter.setColor(255, 0, 0, 255)
paynter.drawLine(100, 350, 900, 350)
paynter.setColor(0, 255, 0, 255)
paynter.drawLine(100, 400, 900, 400)
paynter.setColor(0, 0, 255, 255)
paynter.drawLine(100, 450, 900, 550)

#paynter.drawLine(500, 450, 500, 450)

data[:,:,3] = 255

end = time.time()
print('Execution time: '+str(end-start))






img = Image.fromarray(data, 'RGBA')
img.show()












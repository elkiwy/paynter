import numpy as N
from paynter import *
from PIL import Image

import time



start = time.time()
paynter = Paynter()

pencil = Brush(
	"gradient.png",
	"paperGrain2048.png",
	size=50,
	angle=45,
	spacing=0.05)

watercolor = Brush(
	["watercolor1.png","watercolor2.png","watercolor3.png","watercolor4.png","watercolor5.png"],
	"",
	size=220,
	angle=0,
	spacing = 0.75)

data = N.zeros((2048, 2048, 4), dtype=N.uint8)
data[:,:,3] = 255
data[:,:256,:3] = 255




paynter.setLayer(data)
paynter.setBrush(pencil)
paynter.setColor(0, 0, 0, 255)
paynter.drawLine(100, 100, 1800, 100)
paynter.setColor(255, 255, 255, 255)
paynter.drawLine(100, 200, 1800, 200)

paynter.setBrush(watercolor)
paynter.setColor(255, 0, 0, 255)
paynter.drawLine(100, 350, 1000, 350)
paynter.setColor(0, 255, 0, 255)
paynter.drawLine(100, 400, 1000, 400)
paynter.setColor(0, 0, 255, 255)
paynter.drawLine(100, 450, 1000, 550)

#paynter.drawLine(500, 450, 500, 450)

data[:,:,3] = 255

end = time.time()
print('Execution time: '+str(end-start))






img = Image.fromarray(data, 'RGBA')
img.show()












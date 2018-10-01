import numpy as N
from functions import *
from PIL import Image

import time



start = time.time()
paynter = Paynter()

pencil = Brush("gradient.png","paperGrain2048.png",size=50,angle=45)
#watercolor = Brush(["watercolor1_2.png","watercolor2_2.png","watercolor3_2.png","watercolor4_2.png","watercolor5_2.png"],"",size=220,angle=0)
watercolor = Brush(["watercolor1.png","watercolor2.png","watercolor3.png","watercolor4.png","watercolor5.png"],"",size=220,angle=0)

data = N.zeros((2048, 2048, 4), dtype=N.uint8)
data[:,:,3] = 255
data[:,:256,:3] = 255




paynter.setLayer(data)
paynter.setBrush(pencil)
paynter.setColor(0, 0, 0, 255)
paynter.drawLine(100, 100, 300, 100)
paynter.setColor(255, 255, 255, 255)
paynter.drawLine(100, 200, 300, 200)

paynter.setBrush(watercolor)
paynter.setColor(255, 0, 0, 255)
paynter.drawLine(100, 350, 300, 350)
paynter.setColor(0, 255, 0, 255)
paynter.drawLine(100, 400, 300, 400)
paynter.setColor(0, 0, 255, 255)
paynter.drawLine(100, 450, 300, 450)

paynter.drawLine(500, 450, 500, 450)

data[:,:,3] = 255

end = time.time()
print('Execution time: '+str(end-start))






img = Image.fromarray(data, 'RGBA')
img.show()












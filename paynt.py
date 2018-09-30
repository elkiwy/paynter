import numpy as N
from functions import *
from PIL import Image

import time



start = time.time()
paynter = Paynter()


data = N.zeros((512,512, 4), dtype=N.uint8)
data[:,:,3] = 255
data[:,:256,:3] = 255

paynter.setLayer(data)
paynter.setBrush(Brush("gradient.png","paperGrain.png"))
paynter.setColor(0, 0, 0, 255)
paynter.drawLine(100, 100, 300, 100)
paynter.setColor(255, 255, 255, 255)
paynter.drawLine(100, 200, 300, 200)

paynter.setColor(255, 0, 0, 255)
paynter.drawLine(100, 350, 300, 350)
paynter.setColor(0, 255, 0, 255)
paynter.drawLine(100, 400, 300, 400)
paynter.setColor(0, 0, 255, 255)
paynter.drawLine(100, 450, 300, 450)

data[:,:,3] = 255

end = time.time()
print('Execution time: '+str(end-start))


img = Image.fromarray(data, 'RGBA')
img.show()












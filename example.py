#PaYnter Modules
from paynter import *
import config


#Setup config
config.REAL_CANVAS_SIZE = 2048
config.DEBUG = False
config.DOWNSAMPLING = 1

#Create the paynter and get the image
paynter = Paynter()
image = paynter.image

#Create a palette
palette = getColors_Triad(spread = 20)
palette[0] = tweakColorVal(palette[0], -0.9)
palette[1] = tweakColorSat(palette[1], -0.65)
palette[2] = tweakColorSat(palette[2], -0.65)

#Create the brushes
pencil = Brush( "gradient.png", "paperGrain.png", size=50, angle=45, spacing=0.02)
watercolor = Brush( ["watercolor1.png","watercolor2.png","watercolor3.png","watercolor4.png","watercolor5.png"], "", size=440, angle=0, spacing = 0.5, fuzzyDabAngle = [0, 360], fuzzyDabSize = [1, 2], fuzzyDabHue = [-0.03, 0.03], fuzzyDabSat = [-0.2, 0.2], fuzzyDabVal = [-0.1, 0.1], fuzzyDabMix = [0.4, 0.5], fuzzyDabScatter = [0, 300])

#Fill layer with base color
paynter.fillLayerWithColor(palette[0])

#Create a new layer and draw on it with the waterbrush
image.newLayer()
paynter.setBrush(watercolor)
paynter.setColor(palette[1])
paynter.drawLine(0, config.REAL_CANVAS_SIZE/2, config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE/2)

paynter.setColor(palette[2])
paynter.drawLine(0, config.REAL_CANVAS_SIZE/1.5, config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE/1.5)

#Create a new layer
image.newLayer(effect='lighten')
paynter.setBrush(pencil)
paynter.setColor(palette[2])
paynter.drawLine(100,100,500,200)
paynter.drawLine(100,200,500,300)
paynter.drawLine(100,300,500,400)



pointList = []
pointList.append([300,300])
pointList.append([400,300])
pointList.append([400,400])
pointList.append([300,400])
pointList.append([300,300])
paynter.drawPath(pointList)

paynter.drawRect(500, 300, 600, 400)

paynter.drawRect(700, 300, 800, 400, 45)





#Render the final image
paynter.renderImage()





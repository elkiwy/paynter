#PaYnter Modules
from paynter import *

#Setup config
config.REAL_CANVAS_SIZE = 2048
config.DOWNSAMPLING = 2

#Create the paynter and get the image
paynter = Paynter()

#Create a palette
palette = getColors_Triad(spread = 20)
palette[0].tweak_Val(-0.9)
palette[1].tweak_Sat(-0.65)
palette[2].tweak_Sat(-0.65)

#Create the brushes
pencil = Brush( "gradient3x.png", "paperGrain_dark.png", size=50, angle=45, spacing=0.02)
watercolor = Brush( ["watercolor1.png","watercolor2.png","watercolor3.png","watercolor4.png","watercolor5.png"], "", size=440, angle=0, spacing = 0.5, fuzzyDabAngle = [0, 360], fuzzyDabSize = [1, 2], fuzzyDabHue = [-0.03, 0.03], fuzzyDabSat = [-0.2, 0.2], fuzzyDabVal = [-0.1, 0.1], fuzzyDabMix = [0.4, 0.5], fuzzyDabScatter = [0, 100])

#Fill layer with base color
paynter.fillLayerWithColor(palette[0])

#Create a new layer and draw on it with the waterbrush
paynter.newLayer()
paynter.setBrush(watercolor)
paynter.setColor(palette[1])
paynter.drawLine(0, config.REAL_CANVAS_SIZE/2, config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE/2)

#Create a new layer with lighten blendmode
paynter.newLayer(effect='lighten')
paynter.setColor(palette[2])
paynter.drawLine(0, config.REAL_CANVAS_SIZE/1.5, config.REAL_CANVAS_SIZE, config.REAL_CANVAS_SIZE/1.5)

#Now let's draw with our pencil
paynter.newLayer()
paynter.setBrush(pencil)
paynter.setColor(palette[2])
paynter.drawLine(100,100,500,200)
paynter.drawLine(100,200,500,300)
paynter.drawLine(100,300,500,400)


#Let's activate the mirroring horizontally and vertically
paynter.setMirrorMode('hv')

#We can also use more complex drawing functions like drawPath and drawRect.. Or you can use those as an example to make yours own functions!
paynter.newLayer(effect='overlay')
pointList = []
pointList.append([300,500])
pointList.append([400,500])
pointList.append([400,600])
pointList.append([300,600])
pointList.append([300,500])
paynter.drawPath(pointList)
paynter.drawRect(500, 500, 600, 600)
paynter.drawRect(700, 500, 800, 600, 30)

#Here we add a border to our image and duplicate the current layer to make the overlay blend mode stronger
paynter.addBorder(30)
paynter.duplicateActiveLayer()
paynter.duplicateActiveLayer()


#Render the final image
paynter.renderImage()





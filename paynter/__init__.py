#Import all the paynter modules
import time

start = time.time()
from .brush import *
from .paynter import *
from .layer import *
from .image import *
from .color import *
from .blendModes import *
import paynter.config as config
print('import time:'+str(time.time()-start))
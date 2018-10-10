'''
This file is a custom and more compact version of 'blend_modes' made by Florian Roscheck.
You can find more about it here at https://pythonhosted.org/blend_modes/
'''

import numpy as np



def mergeImagesWithBlendMode(img_in, img_out, blendMode):
    #Take the 0-255 input and convert to 0-1 range
    img_in /= 255
    img_layer /= 255.0
    img_out = 0

    #Compose alpha 
    comp_alpha = np.minimum(img_in[:, :, 3], img_layer[:, :, 3])*opacity
    new_alpha = img_in[:, :, 3] + (1.0 - img_in[:, :, 3])*comp_alpha
    np.seterr(divide='ignore', invalid='ignore')
    ratio = comp_alpha/new_alpha
    ratio[ratio == np.NAN] = 0.0

    #Soft light
    if blendMode=='soft_light':
        comp = (1.0 - img_in[:, :, :3]) * img_in[:, :, :3] * img_layer[:, :, :3] \
                   + img_in[:, :, :3] * (1.0 - (1.0-img_in[:, :, :3])*(1.0-img_layer[:, :, :3]))
    
    #Lighten only    
    elif blendMode=='lighten_only':
        comp = np.maximum(img_in[:, :, :3], img_layer[:, :, :3])

    #Screen
    elif blendMode=='screen':
        comp = 1.0 - (1.0 - img_in[:, :, :3]) * (1.0 - img_layer[:, :, :3])

    #Dodge
    elif blendMode=='dodge':
        comp = np.minimum(img_in[:, :, :3]/(1.0 - img_layer[:, :, :3]), 1.0)

    #Addition
    elif blendMode=='addition':
        comp = img_in[:, :, :3] + img_layer[:, :, :3]

    #Darken only
    elif blendMode=='darken_only':
        comp = np.minimum(img_in[:, :, :3], img_layer[:, :, :3])

    #Multiply
    elif blendMode=='multiply':
        comp = np.clip(img_layer[:, :, :3] * img_in[:, :, :3], 0.0, 1.0)

    #Hard light
    elif blendMode=='hard_light':
         comp = np.greater(img_layer[:, :, :3], 0.5)*np.minimum(1.0-((1.0 - img_in[:, :, :3]) * (1.0 - (img_layer[:, :, :3] - 0.5) * 2.0)), 1.0) \
           + np.logical_not(np.greater(img_layer[:, :, :3], 0.5))*np.minimum(img_in[:, :, :3] * (img_layer[:, :, :3] * 2.0), 1.0)

    #Difference
    elif blendMode=='difference':
        comp = img_in[:, :, :3] - img_layer[:, :, :3]
        comp[comp < 0.0] *= -1.0

    #Subtract    
    elif blendMode=='subtract':
        comp = img_in[:, :, :3] - img_layer[:, :, :3]

    #Grain extract
    elif blendMode=='grain_extract':
        comp = np.clip(img_in[:, :, :3] - img_layer[:, :, :3] + 0.5, 0.0, 1.0)

    #Grain merge
    elif blendMode=='grain_merge':
        comp = np.clip(img_in[:, :, :3] + img_layer[:, :, :3] - 0.5, 0.0, 1.0)

    #Divide
    elif blendMode=='divide':
        comp = np.minimum((256.0 / 255.0 * img_in[:, :, :3]) / (1.0 / 255.0 + img_layer[:, :, :3]), 1.0)

    #Overlay
    elif blendMode=='overlay':
        comp = img_in[:,:,:3] * (img_in[:,:,:3] + (2 * img_layer[:,:,:3]) * (1 - img_in[:,:,:3]))

    
    #Compose img_out
    ratio_rs = np.reshape(np.repeat(ratio, 3), [comp.shape[0], comp.shape[1], comp.shape[2]])
    img_out = np.clip(comp * ratio_rs + img_in[:, :, :3] * (1.0 - ratio_rs), 0.0, 1.0)
    img_out = np.nan_to_num(np.dstack((img_out, img_in[:, :, 3])))  # add alpha channel and replace nans
    return img_out*255.0






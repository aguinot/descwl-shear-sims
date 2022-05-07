#import lsst.afw.image as afw_image


FLAG_CR = 64
FLAG_BAD = 128
FLAG_SAT = 256

def get_flagval(name):
    #return afw_image.Mask.getPlaneBitMask(name)

    if name == 'CR':
        return FLAG_CR
    elif name == 'BAD':
        return FLAG_BAD
    elif name == 'SAT':
        return FLAG_SAT

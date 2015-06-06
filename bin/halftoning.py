r'''
    Module containing halftoning methods for PIL images.

    The idea behind this module is to contain the functions and related options
    for halftoning PIL images. This is a WIP module and I plan to add more 
    features to it over time.
    
    Currently, the halftoning function has an average colour option using the
    'AVERAGE_COLOUR' variable in the module. This only works on the colour of
    the circles drawn and not the background since you can't take an average
    colour for the background of the circles.
    
    Functions that are included are the halftoning function itself which does 
    the halftoning process.
    
    Here is an example of how the Halftoning code works:
    
        >>> f = 'lena.png'
        >>> try:
        ...     img = Image.open(f)
        ... except IOError:
        ...     img = Image.new('RGB', (500,500))
        ...     pix = img.load()
        ...     colRatio = 255.0/img.size[0]
        ...     for x in xrange(img.size[0]):
        ...             for y in xrange(img.size[1]):
        ...                     pix[x,y] = (int(x*colRatio),0,int(y*colRatio))
        ...     img.show(command='display')
        ...
        >>> halfBW = halftoning(img, 15, 1, 4, BLACK_ON_WHITE)
        >>> halfBW.show(command='display')
        >>> halfWB = halftoning(img, 15, 1, 4, WHITE_ON_BLACK)
        >>> halfWB.show(command='display')
        >>> halfAVGW = halftoning(img, 15, 1.5, 4, AVERAGE_COLOUR_ON_WHITE)
        >>> halfAVGW.show(command='display')
        >>> halfAVGB = halftoning(img, 15, 0.5, 4, AVERAGE_COLOUR_ON_BLACK)
        >>> halfAVGB.show(command='display')
        >>> halfCust = halftoning(img, 5, 1, 4, (AVERAGE_COLOUR, (36,103,145)))
        >>> halfCust.show(command='display')
        >>>

    To test/execute the examples in the module documentation make sure that 
    you have imported the halftoning module and do the following:
    import doctest
    nfail, ntests = doctest.testmod(halftoning)
    
'''
from PIL import Image
import PILAddons as pila
import colour as c

AVERAGE_COLOUR = 'AVERAGE_COLOUR'
BLACK_ON_WHITE = ((0,0,0), (255,255,255))
WHITE_ON_BLACK = ((255,255,255), (0,0,0))
AVERAGE_COLOUR_ON_WHITE = (AVERAGE_COLOUR,  (255,255,255))
AVERAGE_COLOUR_ON_BLACK = (AVERAGE_COLOUR, (0,0,0))


def halftoning(img, box, cRatio=1, aalias=4, colour=BLACK_ON_WHITE):
    '''Creates a halftoned PIL Image.
    
    Parameters:
        img [PIL Image] : This is a PIL image object. The image will be 
                          converted to an RGB image.
        box [int]       : The width and height of the box area which will be
                          sampled for its luminosity and a circle created in 
                          its place.
        cRatio [float]  : The circle ratio for the image. If this value is 
                          above 1, the the circles drawn will be scaled up to 
                          overlap each other my that ratio amount. The same
                          will happen for values below 1 by scaling down.
        aalias [int]    : The anti-alias amount for the edges of the circles
                          drawn.
        colour [tuple]  : A 2-tuple containing the foreground colour and
                          background colour in the format (foreground,background).
                          Currently accepts RGB colours and 'AVERAGE_COLOUR' for
                          the foreground. Foreground is the colour of the 
                          cirlces that will be drawn.
    
    On Exit:
        Draws circles within relative size dependent on the luminosity of the
        pixels in the area 'box', and also dependent on the circle ratio 
        'cRatio' and the colour of the circles and background from 'colour' and
        the amount of anti-alias from 'aalias'.
    
        
    '''
    if box <= 0:
        raise ValueError('the value for box must be greater than 0')
    if aalias <= 0:
        raise ValueError('the value for the aalias must be greater than 0')
    
    if not(isinstance(colour, (tuple,list))):
        raise ValueError('the colour flag is not a list of tuple')
    try:
        if colour[1] == AVERAGE_COLOUR:
            raise ValueError('the background colour can not be an average colour')
        if colour[0] != AVERAGE_COLOUR:
            for col in colour:
                c.rgb_check(col)
        else:
            c.rgb_check(colour[1])
    except ValueError as e:
        raise ValueError, "colour is incorrect: {0}".format(e.args[0])
    
    img = img.convert('RGB')
    imgPix = img.load()
    
    htImg = Image.new('RGB', tuple(i*aalias for i in img.size), colour[1])
    bgColourLumin = c.luminosity(colour[1]) # Background colour luminosity
    
    htDraw = pila.Draw(htImg)
    
    for i,x in enumerate(xrange(box/-2, img.size[0], box)):
        col = 0 if i % 2 == 0 else box/2
        for y in xrange(box/-2, img.size[1], box):
            pixelColours = []
            for v in xrange(x, x+box):
                for n in xrange(y,y+box+col):
                    try:
                        pixelColours.append(imgPix[v,n])
                    except IndexError:
                        # This is so that an error isn't raised when pixels
                        # Outside the image range are queried.
                        pass 
                             
            if len(pixelColours) != 0:
                # Create luminosity values for each of the rgb values in pixelColours
                boxLumins = tuple(c.luminosity(rgb) for rgb in pixelColours)
                
                if colour[0] == AVERAGE_COLOUR:
                    finCol = c.average_colours(pixelColours)
                else:
                    finCol = colour[0]
                    
                # This is the luminosity average of the all pixels in the box area
                luminAverage = float(sum(boxLumins))/len(boxLumins)
                
                # This checks if the backgound colour's luminosity is less than
                # less then half grey and creates a circle with radius for
                # if the background is dark of light
                if bgColourLumin >= 127:
                    rad = ((1 - luminAverage / 255.0)*box*aalias/2)*(1.25*cRatio)
                else:
                    rad = ((luminAverage / 255.0 )*box*aalias/2)*(1.25*cRatio)
                
                # Centre point of the circle for the aaliased image
                cp = (((x+box/2))*aalias,((y+box/2+col))*aalias)
                
                htDraw.cp_circle(cp, rad, finCol)
    
    return htImg.resize(img.size, resample=Image.ANTIALIAS)

if __name__ == "__main__":
    f = 'lena.png'
    try:
        img = Image.open(f)
    except:
        img = Image.new('RGB', (512,512))
        pix = img.load()
        colRatio = 255.0/img.size[0]
        for x in xrange(img.size[0]):
            for y in xrange(img.size[1]):
                pix[x,y] = (int(x*colRatio),0,int(y*colRatio))
        img.show(command='display')

    halfBW = halftoning(img, 15, 1, 4, BLACK_ON_WHITE)
    halfBW.show(command='display')
     
    halfWB = halftoning(img, 15, 1, 4, WHITE_ON_BLACK)
    halfWB.show(command='display')
     
    halfAVGW = halftoning(img, 8, 1, 4, AVERAGE_COLOUR_ON_WHITE)
    halfAVGW.show(command='display')
    halfAVGW.save('halftoning.jpg')
     
    halfAVGB = halftoning(img, 15, 0.5, 4, AVERAGE_COLOUR_ON_BLACK)
    halfAVGB.show(command='display')
     
    halfCust = halftoning(img, 5, 1, 4, (AVERAGE_COLOUR, (36,103,145)))
    halfCust.show(command='display')

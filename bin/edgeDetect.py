r'''
    Module containing edge detect methods in the PIL library.

    The idea behind this module is to compile a seleciton of edge detect 
    methods to be used on PIL Images. This is very much a WIP module and will
    be added to as more compatibility is introduced as well as more features.
    
    Currently, the only edge detect method that has been implemented is Canny
    Edge Detect. However, since this is currently the best approach to edge
    detection so few additions will be made to this module overtime. The 
    inclusion of different approaches to the Canny Edge Detect method may be 
    included over time.
    
    Since the project needed the use of 2D arrays for comparing pixels and 
    since the Linux machines at Bournemouth University don't have Numpy and
    Scipy installed, I implemented a technique without installing these modules 
    using nested dictionaries. The 2D arrays used in this module are created 
    using dict_array() which, on default, will create a dictionary when
    called. This means values can be assigned to the 2D array without the
    need for key check statements. For example:
        
        >>> colArray = dict_array()
        >>> for x in xrange(1,101):
        ...     for y in xrange(1,101):
        ...             colArray[x][y] = (255*x/100, 255*y/100, 255*x/y/200)
        ...
        >>> colArray[10][50]
        (25, 127, 0)
        >>>
    
    Functions that are included are traversing adjacent pixels for linking
    edge pixels, a Sobel Pixel Desnsity calculator which is used to calculate
    the gradient of a pixel dependent on the directional Sobel, a find max 
    value for a dictionary array, the creation of a zeroes 2d dict array
    and the actual Canny Edge Detection function itself.
    
    Here is an example of how the Canny Edge Detect code works:
    
        >>> f = 'lena.png'
        >>> try:
        ...     img = Image.open(f)
        ...     fileImg = True
        ... except IOError:
        ...     img = Image.new('RGB', (500, 500))
        ...     drw = ImageDraw.Draw(img)
        ...     drw.ellipse((50, 50, 100, 100), fill=(255, 0, 0))
        ...     drw.rectangle((75,75,125,125), fill=(255,255,0))
        ...     fileImg = False
        ...
        >>> if fileImg:
        ...     edgImg = canny_edge_detection(img)
        ... else:
        ...     edgImg = canny_edge_detection(img, sigma=1)
        ...
        >>> img.show(command='display')
        >>> edgImg.show(command='display')
        >>>
    
    To test/execute the examples in the module documentation make sure that 
    you have imported the edgeDetect module and do the following:
    import doctest
    nfail, ntests = doctest.testmod(edgeDetect)
    
'''

import copy
import math
from PIL import Image, ImageFilter, ImageDraw
from collections import defaultdict
import PILAddons as pila

SOBEL_X = ((-1, 0, 1),
           (-2, 0, 2),
           (-1, 0, 1))

SOBEL_Y = ((-1,-2,-1),
           ( 0, 0, 0),
           ( 1, 2, 1))

def traverse(coX, coY, edgH, edgL, lineCol):
    '''Used to check all the adjacent pixels of an assured edge pixel and check 
    if the pixel from the lower threshold image is an edge, and set that pixel
    to be an edge.
    
    Parameters:
        coX [int]        : Coordinate-X for the pixel on the image.
        coY [int]        : Coordinate-Y for the pixel on the image.
        edgeH [2d array] : The 2d array for the higher threshold edge image.
        edgeL [2d array] : The 2d array for the lower threshold edge image.
        lineCol          : The line colour for the edges.
        
    On Exit:
        Mark as valid edge pixels all the weak pixels in 'edgeL' that are 
        adjacent to the pixel at position [x,y] and are not a valid edge in
        'edgeH'.
    
    '''
    for x,y in pila.adjacent_pixels(coX, coY):
        if edgH[x][y]==0 and edgL[x][y]!=0:
            edgH[x][y]=lineCol+(255,)
            traverse(x, y, edgH, edgL, lineCol)

def round_degrees(deg):
    '''Rounds the degrees to be either horizontal, vertical or diagonal.
    
    Parameters:
        deg [float][int] : The degrees of the angle of the line. Must be 
                           above 0 and range from 0 to 360.
    
    On Exit:
        Returns the degrees rounded to either (0,45,90,135), depending on what
        is closest.
        
    '''
    if deg > 360 or deg < 0:
        raise ValueError,"'{0}' degrees must be between 0 to 360".format(deg)
    
    if (deg<22.5 and deg>=0) or \
       (deg>=157.5 and deg<202.5) or \
       (deg>=337.5 and deg<=360):
        return 0 
    elif (deg>=22.5 and deg<67.5) or \
         (deg>=202.5 and deg<247.5):
        return 45 
    elif (deg>=67.5 and deg<112.5)or \
         (deg>=247.5 and deg<292.5):
        return 90
    else:
        return 135

def sobel_pixel_density(imgPix, x, y, sobel):
    '''Calculates the pixel density/gradient in a 3 x 3 square using the 
    specified by the sobel.
    
    Parameters:
        imgPix [PIL Pixel]  : A PIL Pixel Access object. Created using 
                              Image.load() on a valid PIL image object. Used to
                              get the colour at each pixel position.
        x [int]             : The X-coordinate of the pixel which the centre is
                              for the 3 x 3 sample will be taken from.
        y [int]             : The Y-coordinate of the pixel which the centre is
                              for the 3 x 2 sample will be taken from.
        sobel [list][tuple] : The sobel used to calculate the gradient. These
                              are stored as 'SOBEL_X' and 'SOBEL_Y' in the 
                              module.
                              
    On Exit:
        Either calculates the Y or X gradient for the pixel (dependent on the
        sobel used) and returns the value.
    '''
    pixDen = 0
    for i in xrange(3):
        for j in xrange(3):
            pixDen += sobel[i][j] * imgPix[x-1+j, y-1+i]
    return pixDen


def max_2d_dict_array(dArray):
    '''Finds the maximum value from a 2D dict array.
    
    Parameters:
        dArray [2d array] : The 2D array to which the maximum value is to be 
                            found from.
                            
    On Exit:
        Returns the maximum value contained within the 2d dict array.
    
    '''
    return max(v if not(isinstance(v, defaultdict)) \
               else max_2d_dict_array(v) for v in dArray.itervalues())
    
def min_2d_dict_array(dArray):
    '''Finds the minumum value from a 2D dict array.
    
    Parameters:
        dArray [2d array] : The 2D array to which the minimum value is to be 
                            found from.
                            
    On Exit:
        Returns the minimum value contained within the 2d dict array.
    
    '''
    return min(v if not(isinstance(v, defaultdict)) \
               else min_2d_dict_array(v) for v in dArray.itervalues())


def zeroes_dict_2darray(width, height, value=0):
    '''Creates a complete 2d dict array filled with zeroes or the set value
    'value'.
    
    Parameters:
        width [int]  : The width of the image or number of pixels for the width.
        height [int] : The height of the image or number of pixels for the 
                       height.
        value [any]  : This will fill the entire 2d array with this value as 
                       the default value. The default is zero.
                       
    On Exit:
        Returns a complete 2d dict array filled with the value in 'value'.
        
    '''
    d = dict_array()
    for x in range(width):
        for y in range(height):
            d[x][y] = value
    return d
    
    
def dict_array():
    '''Creates a 2d dictionary array
    
    On Exit:
        Returns a default dictionary object which creates new dictionaries when
        a value is assigned to a key by default. This allows for multiple key
        assignments without checking and creating keys.
        
    '''
    return defaultdict(dict_array)

def img_from_dict_2darry(dArray, mode='RGB'):
    '''Creates a PIL image from a 2d dict array.
    
    Parameters:
        dArray [2d array] : A 2d dict array containing the colour values for 
                            the image.
        mode [string]     : The PIL colour mode for the image.
        
    On Exit:
        Returns a PIL image with the colours values from 'dArray' in the 
        specified colour mode.
    
    '''
    size = dict_2darray_max_size(dArray)
    img = Image.new(mode, size)
    pix = img.load()
    for x,y in pila.pixel_generator(*size):
        pix[x,y] = dArray[x][y]
    return img
        
def dict_2darray_max_size(dArray):
    '''Finds the max value from a 2d dict array
	
    Parameters:
        dArray [2d array] : A 2d dict array containing the colour values for 
                            the image.
                            
    On Exit:
        Returns the maximum value from within the 2d array

    '''
    yKey = (key for val in dArray.itervalues() for key in val.iterkeys() )
    return max(dArray)+1,max(yKey)+1
        
def canny_edge_detection(img, sigma=1.4, thresHigh=0.2, thresLow=0.1, 
                         lineCol=(255,255,255)):
    '''Uses a method of Canny Edge Deteciton to draw the edges of an image.
    
    Parameters:
        img [PIL image]   : a PIL image object
        sigma [float]     : the amount of gaussian blur applied to an image to
                            remove the noise from it.
        thresHigh [float] : the higher threshold boundry for use with edge
                            normalisation and linking.
        thresLow [float]  : the lower threshold boundry for use with edge
                            normalisation and linking.
        lineCol [colour]  : a valid PIL colour. Most common format is a 3-tuple
                            RGB colour.
                            
    On Exit:
        Returns an RGBA image with a black background and the edges of the image
        drawn in the colour 'lineCol' created from the image 'img'.
        
    ''' 
        
    bwImg = img.convert('L') # change image to black and white
    #noNoise = bwImg.filter(ImageFilter.BLUR)
    noNoise = bwImg.filter(ImageFilter.GaussianBlur(sigma))
    #This above line allowes for varying Guassian Blur Levels. However
    #the version of PIL in the labs does not have this implemented, except
    #in newer version. See the documentation for more details.
    pix = noNoise.load() # create a pixel access object for pixel colours
    width, height = img.size

    gradX = zeroes_dict_2darray(*img.size) # create 2d arrays with zeroes
    gradY = zeroes_dict_2darray(*img.size) # the size of the image


    # A 1 pixel offset is used since the first edge slides from the corners of
    # the images due to the Sobel edge detection technique
    for x,y in pila.pixel_generator(width,height, 1,1): 
        px = sobel_pixel_density(pix, x, y, SOBEL_X) 
        py = sobel_pixel_density(pix, x, y, SOBEL_Y) 
        gradX[x][y] = px # stores the gradient intensity at each pixel point
        gradY[x][y] = py # gradX stores the horizontal sobel, gradY the vertical
    
    sobelOutMag = dict_array() # Will store the magnitude of each pixel gradient
    sobelOutDir = dict_array() # Will store the direction of each pixel gradient
    
    for x,y in pila.pixel_generator(width, height):
        sobelOutMag[x][y] = math.hypot(gradX[x][y], gradY[x][y])
        sobelOutDir[x][y] = math.degrees(math.atan2(gradY[x][y], gradX[x][y]))
        if sobelOutDir[x][y] < 0:
            sobelOutDir[x][y] += 360
        # Round each of the grad directions to either horizontal(0), vertical(90)
        # left diagonal(45) or right diagonal(135)
        sobelOutDir[x][y] = round_degrees(sobelOutDir[x][y])
                
    magSup = copy.deepcopy(sobelOutMag)
    
    # For each pixel in the direction matrix, if the corresponding pixels
    # magnitude is less than its diagonals, vertical or horizontal we make that
    # pixel 0.
    for x,y in pila.pixel_generator(width, height, 1,1):
        if sobelOutDir[x][y]==0:
            if (sobelOutMag[x][y]<=sobelOutMag[x+1][y]) or \
               (sobelOutMag[x][y]<=sobelOutMag[x-1][y]):
                magSup[x][y]=0
        elif sobelOutDir[x][y]==45:
            if (sobelOutMag[x][y]<=sobelOutMag[x+1][y+1]) or \
               (sobelOutMag[x][y]<=sobelOutMag[x-1][y-1]):
                magSup[x][y]=0
        elif sobelOutDir[x][y]==90:
            if (sobelOutMag[x][y]<=sobelOutMag[x][y+1]) or \
               (sobelOutMag[x][y]<=sobelOutMag[x][y-1]):
                magSup[x][y]=0 
        else:
            if (sobelOutMag[x][y]<=sobelOutMag[x-1][y+1]) or \
               (sobelOutMag[x][y]<=sobelOutMag[x+1][y-1]):
                magSup[x][y]=0

                 
    maxMag = max_2d_dict_array(magSup) # Maximum value in magSup
    th = thresHigh*maxMag # Higher threshold
    tl = thresLow*maxMag  # lower threshold
    
    edgesHigh = zeroes_dict_2darray(width, height)
    edgesLow = zeroes_dict_2darray(width, height)
    
    for x,y in pila.pixel_generator(width, height):
        # Store pixels with non maximum suppression above th and tl in 
        # edgesHigh and edgesLow respectively
        if magSup[x][y] >= th:
            edgesHigh[x][y] = magSup[x][y]
        if magSup[x][y] >= tl:
            edgesLow[x][y] = magSup[x][y]
        # Normalise the edges by removing all the higher threshold lines from
        # the lower threshold lines image
        edgesLow[x][y] -= edgesHigh[x][y]
    
    
    for x,y in pila.pixel_generator(width, height, 1,1):
        if edgesHigh[x][y]: # If an edge in edgesHigh doesn't = 0
            edgesHigh[x][y]= lineCol+(255,) # Make that pixel the specified line colour
            traverse(x,y,edgesHigh,edgesLow,lineCol) # check adjacent pixels
        else:
            edgesHigh[x][y] = (0,0,0,0)
                
                
    return img_from_dict_2darry(edgesHigh, 'RGBA')
    
    
if __name__ == "__main__":
    f = 'lena.png'
    try:
        img = Image.open(f)
        fileImg = True
    except IOError:
        img = Image.new('RGB', (500,500))
        drw = ImageDraw.Draw(img)
        drw.ellipse((50,50,100,100), fill=(255,0,0))
        drw.rectangle((75,75,125,125), fill=(255,255,0))
        drw.line((500,500,0,0), fill=(0,255,255), width=10)
        fileImg = False
    if fileImg:
        edgImg = canny_edge_detection(img)
    else:
        edgImg = canny_edge_detection(img, sigma=1)
    img.show(command='display')
    edgImg.show(command='display')
    edgImg.save('edgeDetect.png')

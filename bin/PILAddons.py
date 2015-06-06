r'''
    Module containing additional PIL features I have implemented.

    The idea behind this module is to contain useful functions I may use in
    multiple PIL Image projects. This is very much a WIP module and will be 
    added to as I implement more features to the PIL library.
    
    Currently, I have added a function to create a Centre Point Circle 
    to the ImageDraw module to make circle creation easier when having the
    circle dependent on it's position but have varying sized radius. Since I
    will be adding to ImageDraw module here, I simply inherited the current
    ImageDraw.ImageDraw to my ImageDraw class and created a Draw function to
    allow easy implementation. I have also added a PIL colour Palette for use
    with 'P' images. It's primary use is to create complete colour palettes to
    be used with Image.putpalette(Palette.get_palette()).
    
    I have also added an adjacent pixels function which simply returns the 
    adjacent pixels to a specified pixel and also added a pixel generator so 
    that all pixels in an image can be iterated over with edge pixels added or
    removed as required. It also contains a function to convert an RGBA's alpha 
    channel to a grayscale image
    
    Here are some examples of how the code works:
    
        >>> from PIL import Image
        >>> img = Image.new('RGB', (500,500))
        >>> drw = Draw(img)
        >>> pix = img.load()
        >>> colRatio = 255.0/img.size[0]
        >>> for x,y in pixel_generator(*img.size, edgeW=15, edgeH=15):
        ...     pix[x,y] = (int(x*colRatio),0,int(y*colRatio))
        ...
        >>> for x in xrange(40, img.size[0], 60):
        ...     for y in xrange(40, img.size[1], 60):
        ...             for i,j in adjacent_pixels(x,y):
        ...                     pix[i,j] = (int(i*colRatio),int(j*colRatio),128)
        ...
        >>> drw.cp_circle((250,250), 100, (0,255,255), (0,0,0))
        >>> rgb = Palette((0,0,0),(255,255,255),(255,0,255),(255,0,0),(0,0,255))
        >>> rgb(255,255,0)
        (255, 255, 0)
        >>> rgb(0,255,255)
        (0, 255, 255)
        >>> rgb.get_palette()[:9]
        [0, 0, 0, 255, 255, 255, 255, 0, 255]
        >>> qImg = img.convert('P', palette=Image.ADAPTIVE, colors=len(rgb.palette))
        >>> qImg.putpalette(rgb.get_palette(sort=True))
        >>> img.show(command='display')
        >>> qImg.show(command='display')
        
    To test/execute the examples in the module documentation make sure that 
    you have imported the PILAddons module and do the following:
    import doctest
    nfail, ntests = doctest.testmod(PILAddons)
    
'''

from PIL import ImageDraw, Image
import colour as c

class ImageDraw(ImageDraw.ImageDraw):
    
    def cp_circle(self, cpxy, rad, fill=None, outline=None):
        '''Draws a circle from a centre point with the specified radius
        
        Parameters:
            cpxy [tuple][list]   : A two tuple of the pixel location for the 
                                   centre point of the circle on the image.
            rad [int]            : The radius of the circle.
            fill [PIL colour]    : Is a valid PIL readable colour for the fill 
                                   of the circle. This can be any colour used 
                                   by the ImageColor module.
            outline [PIL colour] : Is a valid PIL readable colour for a single 
                                   stroke outline of the circle. This can be 
                                   any colour used by the ImageColor module.
        On Exit:
            Creates a circle with the set radius 'rad' from the centre point 
            'cpxy' with the set fill and outline colours.
            
        '''
        xy = tuple((cpxy[0] + (i*rad), cpxy[1] + (i*rad)) for i in (-1,1))
        self.ellipse(xy, fill=fill, outline=outline)


def Draw(im, mode=None):
    '''A simple 2D drawing interface for PIL images.
    
    Parameters:
        im [PIL Image] : The image to draw in.
        mode [str]     : Optional mode to use for color values.  For RGB
                         images, this argument can be RGB or RGBA (to blend the
                         drawing into the image).  For all other modes, this 
                         argument must be the same as the image mode.  If 
                         omitted, the mode defaults to the mode of the image.
                         
    '''
    try:
        return im.getdraw(mode)
    except AttributeError:
        return ImageDraw(im, mode)
    
    
class Palette:
    '''Stores RGB colours that can be used for a PIL Image colour palette.
    
    Parameters:
        args [tuple][list] : (r,g,b) 3 tuple/list values storing RGB values. 
                             Contains the first colours you wish to store into
                             the palette.
                             
    Attributes:
        palette [list] : Stores the RGB values for the palette.
        
    '''
    def __init__(self, *args):
        self.palette = []
        if len(args) >= 256:
            raise RuntimeError, "too many palette colours have been specified"
        for col in args:
            try:
                c.rgb_check(col)
            except ValueError as e:
                raise ValueError, "incorrect rgb: {0}".format(e.args[0])
            
            if col not in self.palette:
                self.palette.append(col)
        

    def __call__(self, r, g, b):
        '''Maps RGB colours to the colour index.
        
        Parameters:
            r [int] : The value of the red channel.
            g [int] : The value of the green channel.
            b [int] : The value of the blue channel.
            
        On Exit:
            Checks the RGB value and stores it into the palette if there is 
            space.
            
        '''
        rgb = r, g, b
        try:
            c.rgb_check(rgb)
        except ValueError as e:
            raise ValueError, "incorrect rgb: {0}".format(e.args[0])
        
        try:
            return self.palette.index(rgb)
        except:
            i = len(self.palette)
            if i >= 256:
                raise RuntimeError, "all palette entries are used"
            self.palette.append(rgb)
            return rgb

    def get_palette(self, sort=False):
        '''Creates a flattend version of the palette to be read by PIL.
        
        Parameters:
            sort [bool] : If True, then the RGB values will be ordered by 
                          highest value RGB first.
        
        On Exit:
            Returns a list of all the RGB values stored in the palette without 
            being grouped by tuples.
            
        '''
        nPalette = []
        cPalette = self.palette[:]
        if sort:
            cPalette.sort(reverse=True)
            
        for r, g, b in cPalette:
            nPalette.extend([r, g, b])
            
        return nPalette
    

    def get_complete_palette(self, sort=False):
        '''Creates a complete flattend version of the palette to be read by PIL. 
        
        Parameters:
            sort [bool] : If True, then the RGB values will be ordered by 
                          highest value RGB first.
        
        On Exit:
            Returns a list of all the RGB values stored in the palette along 
            with all the empty colours that are stored in a 'P' image without
            being grouped by tuples. This is a series of black RGB colours.
            
        '''
        nPalette = []
        
        cPalette = self.palette[:]
        if sort:
            cPalette.sort(reverse=True)
            
        for r, g, b in cPalette:
            nPalette.extend([r, g, b])
        nPalette.extend([0,0,0]*(256-len(self.palette)))
        
        return nPalette
        
    
def adjacent_pixels(x,y):
    '''Creates a generator for the neighbouring pixels of a set pixel on an 
    image.
    
    Parameters:
        x [int] : The x co-ordinate of the pixel on the image.
        y [int] : The y co-ordinate of the pixel on the image.
        
    On Exit:
        Yields each pixel position surrounding the current pixel at (x,y).
        
    '''
    for i in xrange(-1,2):
        for j in xrange(-1,2):
            if not(i == 0 and j == 0):
                yield x+i,y+j
                
                
def pixel_generator(width, height, edgeW=0, edgeH=0):
    '''Creates a generator for all the pixel locations of an image.
    
    Parameters:
        width [int]  : The width of the image or number of pixels along the x
                       axis.
        height [int] : The height of the image or number of pixels along the y
                       axis.
        edgeW [int]  : Used to set the width edge offset for the pixel 
                       generator. If this is a non-zero value then this number 
                       of pixels from the edge will/will not be included in the 
                       generator.
        edgeH [int]  : Used to set the height edge offset for the pixel 
                       generator. If this is a non-zero value then this number 
                       of pixels from the edge will/will not be included in the 
                       generator.
                       
        On Exit:
            Yields each pixel in the image with the set 'width' and 'height' 
            and will include or exclude the set edge pixels from 'edgeW' and
            'edgeH'.
            
    '''
    for x in xrange(0+edgeW, width-edgeW):
        for y in xrange(0+edgeH, height-edgeH):
            yield x,y
            
            
def convert_rgba_to_mask(img):
    '''Takes the alpha composite of an RGBA image and turns it into a grayscale
    mask image.
    
    Parameters:
        img [PIL Image] : A PIL RGBA Image object
    
    On Exit:
        Returns a grayscale image with each of the values representing the 
        alpha channel of the RGBA image 'img'.
    '''
    mask = Image.new('L', img.size)
    mPix = mask.load()
    iPix = img.load()
    for x,y in pixel_generator(*img.size):
        mPix[x,y] = iPix[x,y][3]
    return mask
            
            
if __name__ == "__main__":
    img = Image.new('RGB', (512,512))
    drw = Draw(img)
    pix = img.load()
    colRatio = 255.0/img.size[0]
    for x,y in pixel_generator(*img.size, edgeW=15, edgeH=15):
        pix[x,y] = (int(x*colRatio),0,int(y*colRatio))
        
    for x in xrange(40, img.size[0], 60):
        for y in xrange(40, img.size[1], 60):
            for i,j in adjacent_pixels(x,y):
                pix[i,j] = (int(i*colRatio),int(j*colRatio),128)
                
    drw.cp_circle((250,250), 100, (0,255,255), (0,0,0))
    rgb = Palette((0,0,0),(255,255,255),(255,0,255),(255,0,0),(0,0,255))
    print rgb(255,255,0)
    print rgb(0,255,255)
    print rgb.get_palette()[:9]
    qImg = img.convert('P', palette=Image.ADAPTIVE, colors=len(rgb.palette))
    qImg.putpalette(rgb.get_palette(sort=True))
    img.show(command='display')
    qImg.show(command='display')

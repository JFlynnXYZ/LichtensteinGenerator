r'''
    Module containing common colour related tasks. This module is frequently 
    used in conjunction with PIL projects.
    
    The idea behind this module is to contain colour related functions which 
    are used when creating images. This is very much a WIP module and will
    be added to as I implement more features necessary for any image or PIL
    related projects.
    
    Currently, most of the functions in this module work with RGB colours and
    not any other types. This will be a feature I will add to the module as 
    it becomes necessary, adding HSV, RGBA, HEX and PIL worded colours. The
    functions included in the module are for checking if an RGB value is valid,
    to unflatten a list of RGB values as well as flatten them, to calculate the
    luminosity of a colour from it's RGB elements, and also average an a list 
    of RGB colours.
    
    Here are some examples of how the code works:
        
        >>> valRGB = (23, 234, 120)
        >>> luminosity(valRGB)
        180.91059999999999
        >>> invRGB = (256,90,123) #Colours only go up to 255
        >>> invRGB2 = (9,0,23.66) #RGB colours can't be float values
        >>> invRGB3 = "(50,100,24)" #String value. Only accept list or tuple
        >>> invRGB4 = (21,200,125,78) #Contains 4 values, only 3 in RGB
        >>> for rgb in (valRGB,invRGB,invRGB2,invRGB3,invRGB4):
        ...     try:
        ...             rgb_check(rgb)
        ...     except ValueError as e:
        ...             e.args[0]
        ...
        "'(256, 90, 123)' can only have an int value between 0 to 255"
        "'(9, 0, 23.66)' rgb can only be integer values, not floats"
        "'(50,100,24)' is not a list or tuple"
        "'(21, 200, 125, 78)' is not 3 numbers long"
        >>> colours = (136,234,90),(32,9,21),(40,39,21),(20,255,78)
        >>> flatCols = rgb_flatten(colours)
        >>> flatCols
        [136, 234, 90, 32, 9, 21, 40, 39, 21, 20, 255, 78]
        >>> rgb_unflatten(flatCols)
        [(136, 234, 90), (32, 9, 21), (40, 39, 21), (20, 255, 78)]
        >>> average_colours(colours)
        (57, 134, 52)
        >>>
        
    To test/execute the examples in the module documentation make sure that 
    you have imported the colour module and do the following:
    import doctest
    nfail, ntests = doctest.testmod(colour)
    
'''
import struct

def rgb2hex(r, g, b):
    '''Used to convert an RGB colour to HEX format for use with Tkinter.
    
    Parameters:
        r [int] : The value of the red channel.
        g [int] : The value of the green channel.
        b [int] : The value of the blue channel.
        
    On Exit:
        Returns a string HEX colour code for the RGB colour.
    '''
    return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)

def hex2rgb(hx):
    '''Used to convert a string HEX colour to RGB format.
    
    Parameters:
        hx [str] : The HEX colour code.
        
    On Exit:
        Returns the RGB colours in a tuple with the values like (R,G,B).
        
    '''
    if hx[0] == '#':
        hx = hx[1:]
    return struct.unpack('BBB',hx.decode('hex'))


def rgb_check(rgb):
    '''Used to check if the value 'rgb' is a valid RGB value.
    
    Parameters:
        rgb [tuple][list][int] : A three tuple list containing the Red, Green 
                                 and Blue values of the RGB colour. Also
                                 accepts a single int value for greyscale
                                 colours, assuming that all the RGB values
                                 are that one value.
                            
    On Exit:
        Will either raise a ValueError, explaining the problem with the RGB
        colour or will pass with no raised error.
    
    '''
    if isinstance(rgb, int):
        if rgb >= 256 or rgb <= -1:
            raise ValueError, "'{0}' can only be an int value between" \
                          " 0 to 255".format(rgb)
        else:
            pass
    else:
        if not isinstance(rgb, (tuple,list)):
            raise ValueError, "'{0}' is not a list or tuple".format(rgb)
        elif len(rgb) != 3:
            raise ValueError, "'{0}' is not 3 numbers long".format(rgb)
        elif any(tuple(True if isinstance(v, float) else False for v in rgb)):
            raise ValueError, "'{0}' rgb can only be integer values, " \
                              "not floats".format(rgb)
        elif any(tuple(True if v >= 256 or v <= -1 else False for v in rgb)):
            raise ValueError, "'{0}' can only have an int value between" \
                              " 0 to 255".format(rgb)
        else:
            pass
    
    
def rgb_unflatten(rgbCols):
    '''Converts a list of separated RGB values into a 3 tuple groups of (R,G,B)
    
    Parameters:
        rgbCols [list][tuple] : A list of separate R,G,B values all being ints.
    
    On Exit:
        Combines and groups every 3 values into it's own tuple and returns a 
        complete list of grouped RGB values.
        
    '''
    return [tuple(rgbCols[i:i+3]) for i in range(0,len(rgbCols),3)]


def rgb_flatten(rgbCols):
    '''Converts a list of grouped RGB values into a single list of RGB values.
    
    Parameters:
        rgbCols [list][tuple] : A list of grouped, 3 tuple RGB values.
    
    On Exit:
        Separates every RGB value into a single list of RGB values.
        
    '''
    rgb = []
    for r, g, b in rgbCols:
        rgb.extend([r, g, b])
    return rgb
    
    
def luminosity(rgb, rcoeff=0.2126, gcoeff=0.7152, bcoeff=0.0722):
    '''Calculates the Luminosity of an RGB value dependent on the RGB 
    coefficiants.
    
    Parameters:
        rgb [list][tuple][int] : Can either be an RGB value or a single int 
                                 value representing a 3 tuple greyscale colour.
        rcoeff [float]         : The Red channel luminosity colour coefficient.
        gcoeff [float]         : The Green channel luminosity colour coefficient.
        bcoeff [float]         : The Blue channel luminosity colour coefficient.
        
    On Exit:
        Returns a float of the luminosity of the colour, ranging from 0 to 255.
        
    '''
        
    if isinstance(rgb, int) and rgb >= 0 and rgb <= 255:
        return float(rgb)
    try:
        rgb_check(rgb)
    except ValueError as e:
        raise ValueError, "the rgb is invalid: {0}".format(e.args[0])
    
    return rcoeff*rgb[0]+gcoeff*rgb[1]+bcoeff*rgb[2]
    
    
def average_colours(colList):
    '''Calculates the average colour from a list of RGB colours.
    
    Parameters:
        colList [tuple][list] : A list of 3 tuple RGB values. Each of these
                                RGB values will be checked when the function
                                is run.
                                
    On Exit:
        Returns the average RGB value as a 3 tuple value in the format (R,G,B).
        
    '''
    if not isinstance(colList, (list, tuple)):
        raise ValueError,'colList must be a list or tuple'
    try:
        for col in colList:
            rgb_check(col)
    except ValueError as e:
        raise ValueError, "an rgb value is incorrect: {0}".format(e.args[0])
    
    tR, tG, tB = [], [], []
    for rgb in colList:
        if isinstance(rgb, int):
            r = g = b = rgb
        else:
            r,g,b = rgb
        tR.append(r)
        tG.append(g)
        tB.append(b)
    return sum(tR)/len(tR), sum(tG)/len(tG), sum(tB)/len(tB)


if __name__ == "__main__":
    valRGB = (23, 234, 120) #Valid RGB value
    print luminosity(valRGB)
    invRGB = (256, 90, 123) #Colours only go up to 255
    invRGB2 = (9, 0, 23.66) #RGB colours can't have a float in
    invRGB3 = "(50, 100, 24)" #String value. Only accept list or tuple
    invRGB4 = (21, 323, 432, 432) #Contains 4 values. Only 3 allowed
    for rgb in (valRGB,invRGB,invRGB2,invRGB3,invRGB4):
        try:
            rgb_check(rgb)
        except ValueError as e:
            print e.args[0]
    colours = (136,234,90),(32,9,21),(40,39,21),(20,255,78)
    flatCols = rgb_flatten(colours)
    print flatCols
    uFlatCols = rgb_unflatten(flatCols)
    print uFlatCols
    print average_colours(uFlatCols)
    
r'''
    Module containing Colour Quantization for reducing an images down to a
    selection of set colours.
    
    The idea behind this module is to replace the colours of an image with
    the most likely matches from a set of colours specified by the user. This
    module works in conjunction with PIL as it's means for editing image 
    colours.
    
    Currently, the module only works with RGB colours currently but the 
    use of other PIL colour types will be added in the future, such as HSV,
    RGBA, HEX and PIL worded colours. The functions in the module consist of
    calculating the closeness of a colour to another and switching them using
    colour switch, and the Colour Quantization function itself.
    
    Here are some examples of how the code works:
        
        >>> curCols = [(98,186,25), (50,0,69), (245,89,12), (69,156,102), (89,56,71), (89,58, 205), (5,5,20)]
        >>> newCols = [(0,0,0), (255,255,255), (255,0,0), (0,0,255), (255,255,0)]
        >>> colour_switch(curCols, newCols)
        [(255, 255, 0), (0, 0, 255), (255, 0, 0), (69, 156, 102), (89, 56, 71), (255, 255, 255), (0, 0, 0)]
        >>> f = 'lena.png'
        >>> try:
        ...     img = Image.open(f)
        ... except IOError:
        ...     img = Image.new('RGB', (500,500))
        ...     drw = ImageDraw.Draw(img)
        ...     for i,x in enumerate(xrange(40, img.size[0], 70)):
        ...             for y in xrange(40, img.size[1], 70):
        ...                     drw.rectangle((x-30,y-30,x,y), fill=curCols[i])
        ...
        >>> quantImg = quantize(img, newCols, nCols=len(curCols)+1, sigma=1)
        >>> img.show(command='display')
        >>> quantImg.show(command='display')
        >>>
        
    To test/execute the examples in the module documentation make sure that 
    you have imported the quantize module and do the following:
    import doctest
    nfail, ntests = doctest.testmod(quantize)
    
'''
from PIL import Image, ImageFilter, ImageDraw
import colour as c


def colour_switch(curC, newC):
    '''Switches the closest matching colours from one list of colours to 
    another, creating a combined palette of colours.
    
    Parameters:
        curC [list] : a list of 3-tuple RGB colours. These are colours that 
                      are from the current image and will be switched out for
                      the closest matching colour from 'newC'.
        newC [list] : a list of 3-tuple RGB colours. These are the colours 
                      which will replace there closest matching counter colour
                      in the list 'curC'
                      
    On Exit:
        Returns a new combined list of colours with all the 'newC' colours
        replacing there closest matching colours from 'curC'. If there are less
        new colours compared to current colours, then any colours which have
        no close new colour counterpart will be left in the colours.
        
    '''
    if len(newC) > len(curC):
        raise ValueError, "more values are in new colours over current colours"
    cCloseness = {}
    for cCol in curC:
        cCloseness[cCol] = {}
        for nCol in newC:
            cCloseness[cCol][nCol] = sum([abs(cCol[i]-nCol[i]) for i in range(3)])

    finalPalette = curC[:]
    for newColour in newC:
        curCol, close = None, 766
        for currentColour, comparisons in cCloseness.items():
            if comparisons[newColour] < close:
                curCol, close = currentColour, comparisons[newColour]

        finalPalette[finalPalette.index(curCol)] = newColour
        del cCloseness[curCol]

    return finalPalette

def quantize(img, newCols, nCols=8, sigma=4, aalias=4):
    '''Creates a colour quantize image from a PIL Image with new colours.
    
    Parameters:
        img [PIL Image] : A PIL image object. Any colour mode can be used but
                          RGB is preferred.
        newCols [list]  : A list of 3-tuple RGB colours to replace there 
                          closest matching colour on the image.
        nCols [int]     : The number of colours that the image will be reduced
                          to. This number must be higher then the length of
                          'newCols'.
        sigma [float]   : The magnitude of the gaussian blur used on the image
                          to de-noise the image for a smoother result.
        aalias [int]    : The anti-alias amount for the edges of the pixels.
        
    On Exit:
        Returns an RGB PIL image with the number of colours 'nCols', with the
        colours from 'newCols' replacing their closest matches from the image,
        as well as a noise reduction of 'sigma' and anti alias of 'aalias'.
        
    '''
    aaliasImg = img.resize((img.size[0]*aalias, img.size[1]*aalias), 
                           resample=Image.ANTIALIAS)
    #aaliasImg = aaliasImg.filter(ImageFilter.GaussianBlur(sigma))
    #This above line allowes for varying Guassian Blur Levels. However
    #the version of PIL in the labs does not have this implemented, except
    #in newer version. See the documentation for more details.
    aaliasImg = aaliasImg.filter(ImageFilter.BLUR)
    
    finImg = aaliasImg.convert("P", palette=Image.ADAPTIVE, colors=nCols)
    
    curCols = c.rgb_unflatten(finImg.getpalette()[:3*nCols])
    
    finalPalette = colour_switch(curCols, newCols)
    
    finImg.putpalette(c.rgb_flatten(finalPalette))
    
    finImg = finImg.resize(img.size, resample=Image.ANTIALIAS)
    return finImg.convert('RGB')


if __name__ == '__main__':
    curCols = [(98,186,25), (50,0,69), (245,89,12), (69,156,102), (89,56,71), 
               (89,58, 205), (5,5,20)]
    newCols = [(0,0,0), (255,255,255), (190,0,0), (0,16,115), (248,196,0)]
    print colour_switch(curCols, newCols)
    f = 'lena.png'
    try:
        img = Image.open(f)
    except IOError:
        img = Image.new('RGB', (512,512))
        drw = ImageDraw.Draw(img)
        for i,x in enumerate(xrange(40, img.size[0], 70)):
            for y in xrange(40, img.size[1], 70):
                drw.rectangle((x-30,y-30,x,y), fill=curCols[i])
    quantImg = quantize(img, newCols, nCols=len(curCols)+1, sigma=1)
    img.show(command='display')
    quantImg.show(command='display')
    

r'''
    Module for creating Roy Lichtenstein style images generator which creates
    images from a PIL Image.
    
    Each image is created using 3 different modules consisting of halftoning,
    edgeDetect and quantize. They are all used together to create the final
    product.
    
    Here is an example of how the code works:
    
        >>> f = 'lena.png'
        >>> try:
        ...     img = Image.open(f)
        ... except IOError:
        ...     img = Image.new('RGB', (512,512))
        ...     pix = img.load()
        ...     drw = pila.Draw(img)
        ...     colRatio = 255.0/img.size[0]
        ...     for x,y in pila.pixel_generator(*img.size, edgeW=15, edgeH=15):
        ...         pix[x,y] = (int(x*colRatio),0,int(y*colRatio))
        ...     drw.cp_circle((250,250), 100, (0,255,255))
        ...     img.show(command='display')
        ...
        >>> lichtenstein(img).show(command='display')
        >>> nCols = [(0,0,0),(255,255,255),(239,228,176),(128,0,128),(228,122,121)]
        >>> lichtenstein(img, nCols, qtNCols=6, edColour=(255,0,0), htBox=15).show(command='display')
        >>> nCols2 = [(83,31,72),(255,241,191),(38,22,184),(233,95,113),(190,159,163)]
        >>> htCol = (ht.AVERAGE_COLOUR, (80,50,90))
        >>> edCol = (12,163,243)
        >>> lichtenstein(img, nCols2, qtNCols=16, edColour=edCol, htColour=htCol).show(command='display')
        >>>
    
    To test/execute the examples in the module documentation make sure that 
    you have imported the lichtenstein module and do the following:
    import doctest
    nfail, ntests = doctest.testmod(lichtenstein)
    
'''
from PIL import Image
import PILAddons as pila
import PIL.ImageOps as ImageOps
import halftoning as ht
import edgeDetect as ed
import quantize as qt


DEFAULT_COLOURS = ((0,0,0), (255,255,255), (190,0,0), (0,16,115), (248,196,0))

def lichtenstein(img, qtNewCols=DEFAULT_COLOURS, qtSigma=4, qtNCols=8,
                edSigma=1.4, edThresH=0.2, edThresL=0.1, edColour=(0,0,0),
                htBox=8, htColour=ht.AVERAGE_COLOUR_ON_WHITE, htCRatio=1,
                aalias=2):
    '''Generates a Roy Lichtenstein RGB PIL image from a PIL image.
    
    Parameters:
        img [PIL Image]   : a PIL Image object. Best results are created from
                            RGB images.
        qtNewCols [tuple] : a tuple of 3-tuple RGB values which will be the 
                            new colours for the quantize process
        qtSigma [float]   : the magnitude for the gaussian blur used to reduce
                            the noise for the quantize process
        qtNCols [int]     : the number of colours used to reduce the image to
                            for the quantize process
        edSigma [float]   : the magnitude for the gaussain blur used to recduce
                            the noise for the edge detect process
        edThresH [float]  : the higher threshold boundry used for edge linking
                            and normalisation for the edge detect process
        edThresL [float]  : the lower threshold boundry used for edge linking
                            and normalisation for the edge detect process
        edColour [tuple]  : the RGB colour for the edges created by the edge
                            detect process
        htBox [int]       : the halftoning box width and height used for the
                            area of pixels a sample of luminosity values
        htColour [tuple]  : a 2-tuple containing the foreground colour and
                            background colour for the halftoning circles. Must
                            be RGB values or 'ht.AVERAGE_COLOUR'
        htCRatio [float]  : the circle ratio used for drawing the circles in 
                            the halftoning process so that they can be overall 
                            bigger or smaller in scale
        aalias [int]      : The anti-alias amount for the edges of all the 
                            processes
                            
        On Exit:
            Generates a Roy Lichtenstein image and returns an RGB PIL image.
        
        '''
    img = img.convert('RGB')
    quantImg = qt.quantize(img, qtNewCols, qtNCols, qtSigma, aalias)
    halfImg = ht.halftoning(quantImg, htBox, htCRatio, aalias, htColour)
    edgeImg = ed.canny_edge_detection(img, edSigma, edThresH, edThresL, edColour)
    
    edgeMask = ImageOps.invert(pila.convert_rgba_to_mask(edgeImg))
    
    halfMask = Image.new('1', img.size)
    
    halfMaskPix = halfMask.load()
    quantPix = quantImg.load()
    
    # Create a mask for the halftoning, making it visible where the colours
    # are still the orignal adaptive colours and not the new ones.
    for x,y in pila.pixel_generator(*img.size):
        if quantPix[x,y] in qtNewCols:
            halfMaskPix[x,y] = 1
        else:
            halfMaskPix[x,y] = 0
            
    compQuHt = Image.composite(quantImg, halfImg, halfMask) # Combine quant and half
    finalImg = Image.composite(compQuHt, edgeImg, edgeMask) # Combine compQuHt and edge
    return finalImg.convert('RGB')
        
        
if __name__ == "__main__":
    f = 'lena.png'
    try:
        img = Image.open(f)
    except IOError:
        img = Image.new('RGB', (512,512))
        pix = img.load()
        drw = pila.Draw(img)
        colRatio = 255.0/img.size[0]
        for x,y in pila.pixel_generator(*img.size, edgeW=15, edgeH=15):
            pix[x,y] = (int(x*colRatio),0,int(y*colRatio))
        drw.cp_circle((250,250), 100, (0,255,255), (0,0,0))
        img.show(command='display')
        
    lichtenstein(img).save('lichtenstein.jpg')
    
    nCols = [(0,0,0),(255,255,255),(239,228,176),(128,0,128),(228,122,121)]
    lichtenstein(img, nCols, qtNCols=6, edColour=(255,0,0), htBox=15).show(command='display')
    
    nCols2 = [(83,31,72),(255,241,191),(38,22,184),(233,95,113),(190,159,163)]
    htCol = (ht.AVERAGE_COLOUR, (80,50,90))
    edCol = (12,163,243)
    lichtenstein(img, nCols2, qtNCols=16, edColour=edCol, htColour=htCol).show(command='display')

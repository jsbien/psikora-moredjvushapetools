# -*- coding: utf-8 -*-
"""
Based on pyWiki 'Working With Images' @  http://wiki.wxpython.org/index.cgi/WorkingWithImages
Modified to properly copy, create or remove any alpha in all conversion permutations.
A wx.App must be created in order for the various wx functions to work.

Win32IconImagePlugin  
Alternate PIL plugin for dealing with Microsoft .ico files.
http://code.google.com/p/casadebender/wiki/Win32IconImagePlugin

Note:  The terms "plane", "band", "layer" and "channel" are used interchangibly.

Tested on Win7 64-bit (6.1.7600) and Win XP SP3 (5.1.2600) using Python unicode 32-bit.

Platform  Windows 6.1.7600
Python    2.5.4 (r254:67916, Dec 23 2008, 15:10:54) [MSC v.1310 32 bit (Intel) (x86)]
Python wx 2.8.10.1
Pil       1.1.7

Ray Pasco      
pascor(at)verizon(dot)net

Last modification:      2011-05-15      Added WxImageFromPilImage import.

This code may be freely modified and distributed for any purpose whatsoever.

"""

import wx
import Image             # PIL module. Only if you use the PIL library.

import numpy

def empty_image(width, height, colour = (255,255,255)):
    array = numpy.zeros( (height, width, 3),'uint8')
    array[:,:,] = (colour)
    image = wx.EmptyImage(width, height)
    image.SetData( array.tostring())
    return image
    

def WxBitmapToPilImage( myBitmap ) :
    return WxImageToPilImage( WxBitmapToWxImage( myBitmap ) )

def WxBitmapToWxImage( myBitmap ) :
    return wx.ImageFromBitmap( myBitmap )

#-----

def PilImageToWxBitmap( myPilImage ) :
    return WxImageToWxBitmap( PilImageToWxImage( myPilImage ) )

def PilImageToWxImage( myPilImage ):
    myWxImage = wx.EmptyImage( myPilImage.size[0], myPilImage.size[1] )
    myWxImage.SetData( myPilImage.convert( 'RGB' ).tostring() )
    return myWxImage

# Or, if you want to copy any alpha channel, too (available since wxPython 2.5)
# The source PIL image doesn't need to have alpha to use this routine.
# But, a PIL image with alpha is necessary to get a wx.Image with alpha.

def PilImageToWxImage( myPilImage, copyAlpha=True ) :

    hasAlpha = myPilImage.mode[ -1 ] == 'A'
    if copyAlpha and hasAlpha :  # Make sure there is an alpha layer copy.

        myWxImage = wx.EmptyImage( *myPilImage.size )
        myPilImageCopyRGBA = myPilImage.copy()
        myPilImageCopyRGB = myPilImageCopyRGBA.convert( 'RGB' )    # RGBA --> RGB
        myPilImageRgbData =myPilImageCopyRGB.tostring()
        myWxImage.SetData( myPilImageRgbData )
        myWxImage.SetAlphaData( myPilImageCopyRGBA.tostring()[3::4] )  # Create layer and insert alpha values.

    else :    # The resulting image will not have alpha.

        myWxImage = wx.EmptyImage( *myPilImage.size )
        myPilImageCopy = myPilImage.copy()
        myPilImageCopyRGB = myPilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
        myPilImageRgbData =myPilImageCopyRGB.tostring()
        myWxImage.SetData( myPilImageRgbData )

    return myWxImage

#-----

def imageToPil( myWxImage ):
    myPilImage = Image.new( 'RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()) )
    myPilImage.fromstring( myWxImage.GetData() )
    return myPilImage

def WxImageToWxBitmap( myWxImage ) :
    return myWxImage.ConvertToBitmap()
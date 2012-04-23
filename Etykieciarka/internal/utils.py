'''
Created on Apr 19, 2012

@author: zasvid
'''

import wx
import StringIO

def get_wx_image(shape_image):
    #buf = StringIO.StringIO(shape_image.tostring())
    #return wx.ImageFromStream(buf, wx.BITMAP_TYPE_ANY)
    shape_image.save("shape.png", "png")
    wx_image = wx.Image("shape.png", wx.BITMAP_TYPE_ANY)
    return wx.BitmapFromImage(wx_image)
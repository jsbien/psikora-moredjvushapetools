# -*- coding: utf-8 -*-
'''
    hOCR Labeller of DjVu shapes    
    Copyright (C) 2012 Piotr Sikora

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import wx
import wx.lib.scrolledpanel
from internal.image_conversion import empty_image, PilImageToWxImage

class LinePreviewPanel(wx.lib.scrolledpanel.ScrolledPanel):
    
    def __init__(self, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        self.bitmap = None
        
    def generate_preview(self, line_rect, blits, char):
        panel_width, _ = self.GetSize()
        if self.bitmap is not None:
            #self.sizer.Remove(self.bitmap)
            self.bitmap.Destroy()
        self.left0 = line_rect.x - 2
        #adjust for panel width
        while char.x + char.w + 3 - self.left0 > panel_width:
            self.left0 += 9 * (panel_width/10)
        
        self.top0 = line_rect.y + line_rect.h + 2
        image = empty_image(panel_width, line_rect.h + 4)
        for blit in blits:
            image.Paste(PilImageToWxImage(blit.shape.image), blit.x - self.left0, self.top0 - blit.y - blit.h)
        #draw lines
        line_ver = empty_image(2, char.h + 2, (255,0,0))
        line_hor = empty_image(char.w + 2, 2, (255,0,0))
        image.Paste(line_ver, char.x - self.left0 - 1 , self.top0 - char.y - char.h - 1)
        image.Paste(line_hor, char.x - self.left0 - 1 , self.top0 - char.y - char.h - 1)
        image.Paste(line_ver, char.x - self.left0 + char.w + 1, self.top0 - char.y - char.h - 1)
        image.Paste(line_hor, char.x - self.left0 - 1, self.top0 - char.y + 1)
        self.bitmap = wx.StaticBitmap(self, bitmap = image.ConvertToBitmap())
        self.SetMinSize(self.bitmap.GetSize())
        self.SetupScrolling()
        self.Scroll(char.x - self.left0 - 50, y = 0)
        
        self.Refresh()
        self.Update()
        

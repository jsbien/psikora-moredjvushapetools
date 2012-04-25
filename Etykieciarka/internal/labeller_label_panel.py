# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: Piotr Sikora
'''

import wx
from utils import get_wx_image


class LabelPanel(wx.Panel):
    
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.data = data
        staticbox = wx.StaticBox(self, label = 'Dane kształtu')
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.VERTICAL)
        self.inner_panel = wx.Panel(self)
        sizer.Add(self.inner_panel, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        
    def label_layout(self, sizer, label, value):
        linesizer = wx.BoxSizer(wx.HORIZONTAL)
        infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, label)
        valuelabel = wx.StaticText(self.inner_panel, wx.ID_ANY, value)
        linesizer.Add(infolabel, 0, wx.ALL, 5)
        linesizer.AddStretchSpacer()
        linesizer.Add(valuelabel, 0, wx.ALL, 5)
        sizer.Add(linesizer, 0, wx.ALL | wx.EXPAND, 5)
        #sizer.AddSpacer((5,5),0)

        
    def regenerate(self):
        self.inner_panel.DestroyChildren()
        sizer = wx.BoxSizer(wx.VERTICAL)

        if self.data.current_shape is not None:
            #currentShape = wx.StaticBitmap(self.inner_panel, wx.ID_ANY, get_wx_image(self.data.current_shape.get_image()))
            #sizer.Add(currentShape, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            self.label_layout(sizer, "Dokument:", str(self.data.current_shape.id))
            self.label_layout(sizer, "Nazwa słownika kształtów: ", str(self.data.current_dictionary.name))
            #tu idzie obrazek
            imagepanel = wx.Panel(self.inner_panel)
            imagesizer = wx.BoxSizer(wx.VERTICAL)
            shapeImage = wx.StaticBitmap(imagepanel, -1, get_wx_image(self.data.current_shape.get_image()))
            imagesizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, 5)
            imagepanel.SetSizer(imagesizer)
            sizer.Add(imagepanel, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            
            self.label_layout(sizer, "Numer w słowniku kształtów:", str(self.data.current_shape.id))
            self.label_layout(sizer, "Szerokość x Wysokość:", str(self.data.current_shape.width) + " x " + str(self.data.current_shape.height))
            self.label_layout(sizer, "Rozmiar fontu:", "")
            self.label_layout(sizer, "Krój fontu:", "")
            self.label_layout(sizer, "Postać:", "")
            self.label_layout(sizer, "Typ tekstela:", "")
            self.label_layout(sizer, "Tekstel:", "")
            sizer.AddStretchSpacer(1)
    
        self.inner_panel.SetSizer(sizer, True)
        self.inner_panel.Fit()
        self.inner_panel.Layout()
        self.inner_panel.Refresh()
        self.inner_panel.Update()

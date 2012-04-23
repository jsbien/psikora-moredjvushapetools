# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: zasvid
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
        
        
    def regenerate(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        if self.data.current_shape is not None:
            #currentShape = wx.StaticBitmap(self.inner_panel, wx.ID_ANY, get_wx_image(self.data.current_shape.get_image()))
            #sizer.Add(currentShape, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            
            linesizer = wx.BoxSizer(wx.HORIZONTAL)
            infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, "Numer w słowniku kształtów:")
            valuelabel = wx.StaticText(self.inner_panel, wx.ID_ANY, str(self.data.current_shape.id))
            linesizer.AddStretchSpacer(1)
            linesizer.Add(infolabel, 0, wx.ALL, 5)
            linesizer.AddSpacer((5,5), 0)
            linesizer.Add(valuelabel, 0, wx.ALL, 5)
            linesizer.AddStretchSpacer(1)
            sizer.Add(linesizer, 1, wx.ALL, 5)
            sizer.AddSpacer((5,5),0)

            linesizer = wx.BoxSizer(wx.HORIZONTAL)
            infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, "Szerokość x Wysokość")
            valuelabel = wx.StaticText(self.inner_panel, wx.ID_ANY, str(self.data.current_shape.width) + " x " + str(self.data.current_shape.height))
            linesizer.AddStretchSpacer(1)
            linesizer.Add(infolabel, 1, wx.ALL, 5)
            linesizer.AddSpacer((5,5), 0)
            linesizer.Add(valuelabel, 1, wx.ALL, 5)
            linesizer.AddStretchSpacer(1)
            sizer.Add(linesizer, 1, wx.ALL | wx.ALIGN_CENTER, 5)
            sizer.AddSpacer((5,5),0)

            linesizer = wx.BoxSizer(wx.HORIZONTAL)
            infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, "Nazwa słownika kształtów: ")
            valuelabel = wx.StaticText(self.inner_panel, wx.ID_ANY, str(self.data.current_dictionary.name))
            linesizer.AddStretchSpacer(1)
            linesizer.Add(infolabel, 0, wx.ALL, 5)
            linesizer.AddSpacer((5,5), 0)
            linesizer.Add(valuelabel, 0, wx.ALL, 5)
            linesizer.AddStretchSpacer(1)
            sizer.Add(linesizer, 0, wx.ALL, 5)
            sizer.AddSpacer((5,5),0)

            linesizer = wx.BoxSizer(wx.HORIZONTAL)
            infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, "Dokument:")
            valuelabel = wx.StaticText(self.inner_panel, wx.ID_ANY, str(self.data.current_document.name))
            linesizer.AddStretchSpacer(1)
            linesizer.Add(infolabel, 0, wx.ALL, 5)
            linesizer.AddSpacer((5,5), 0)
            linesizer.Add(valuelabel, 0, wx.ALL, 5)
            linesizer.AddStretchSpacer(1)
            sizer.Add(linesizer, 0, wx.ALL, 5)
            sizer.AddSpacer((5,5),0)

            sizer.AddStretchSpacer(1)
        """
        
        label1 = wx.StaticText(self, wx.ID_ANY, "Rozmiar fontu:")
        label2 = wx.StaticText(self, wx.ID_ANY, "Krój fontu:")
        label3 = wx.StaticText(self, wx.ID_ANY, "Postać:")
        label4 = wx.StaticText(self, wx.ID_ANY, "Typ tekstela")
        label5 = wx.StaticText(self, wx.ID_ANY, "Tekstel:")
        label6 = wx.StaticText(self, wx.ID_ANY, "nazwa tekstela w unicodzie")
        textCtrl1 = wx.TextCtrl(self)
        textCtrl2 = wx.TextCtrl(self)
        textCtrl3 = wx.TextCtrl(self)
        textCtrl4 = wx.TextCtrl(self)
    
        checkboxesSizer = wx.BoxSizer(wx.HORIZONTAL)
        cb1 = wx.RadioButton(self, wx.ID_ANY, "właściwy")
        cb2 = wx.RadioButton(self, wx.ID_ANY, "makrotekstel")
        cb3 = wx.RadioButton(self, wx.ID_ANY, "mikrotekstel")
        checkboxesSizer.Add(cb1, 1, wx.ALIGN_CENTER, 1)
        checkboxesSizer.Add(cb2, 1, wx.ALIGN_CENTER, 1)
        checkboxesSizer.Add(cb3, 1, wx.ALIGN_CENTER, 1)
    
        labelSizer.Add(currentShape , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(label1 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(textCtrl1 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(label2 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(textCtrl2 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(label3 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(textCtrl3 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(label4 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(checkboxesSizer, 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(label5 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(textCtrl4 , 1, wx.ALIGN_CENTER, 1)
        labelSizer.Add(label6 , 1, wx.ALIGN_CENTER, 1)
        """
        self.inner_panel.SetSizer(sizer, True)
        self.Refresh()
        self.Update()

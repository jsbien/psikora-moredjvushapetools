# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: zasvid
'''

import wx
import wx.lib.scrolledpanel
from internal.utils import get_wx_image

class RootPanel(wx.Panel):
    def __init__(self, parent, shape):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.shape = shape
        sizer = wx.BoxSizer(wx.VERTICAL)
        imagePanel = wx.Panel(self)
        imageSizer = wx.BoxSizer(wx.HORIZONTAL)
        shapeImage = wx.StaticBitmap(imagePanel, -1, get_wx_image(self.shape.get_image()))
        imageSizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        imagePanel.SetSizer(imageSizer)
        
        infovalue = shape.count_descendants() + 1
        infotext = str(infovalue)
        if infovalue > 4:
            infotext += ' kształtów.'
        elif infovalue > 1:
            infotext += ' kształy.'
        else:
            infotext += ' kształt.'
        info = wx.StaticText(self, label = infotext)
        
        sizer.Add(imagePanel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(info, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        imagePanel.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    def OnClick(self, event):
        self.select()

    def deselect(self):
        self.SetBackgroundColour(wx.NullColor)
        
    def select(self):
        self.SetBackgroundColour('#00ff00')
        self.parent.data.current_hierarchy = self.shape
        if self.parent.currently_selected_subpanel is not None:
            self.parent.currently_selected_subpanel.deselect()
        self.parent.currently_selected_subpanel = self 
        self.parent.target_panel.regenerate()

class RootsPanel(wx.lib.scrolledpanel.ScrolledPanel):
    
    def __init__(self, parent, data, target_panel):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.data = data
        self.target_panel = target_panel
        self.root_panels = []
        self.prepare_for_new_layout()
        
    def regenerate(self):
        sizer = self.prepare_for_new_layout()
        for panel in self.root_panels:
            panel.Destroy()
        self.root_panels = []
        for hierarchy_root in self.data.shape_hierarchies:
            panel = RootPanel(self, hierarchy_root)
            self.root_panels.append(panel)
            sizer.Add(panel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            sizer.AddSpacer(5)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer, True)
        self.SetupScrolling(scroll_y = False)
        self.Refresh()
        self.Update()
    
    def prepare_for_new_layout(self):
        self.currently_selected_subpanel = None
        staticbox = wx.StaticBox(self, label = 'Korzenie hierarchii kształtów')
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)
        self.SetSizer(sizer, True)
        return sizer

    def select(self, shape):
        for panel in self.root_panels:
            if panel.shape.db_id == shape.db_id:
                panel.select()
                break
        
        
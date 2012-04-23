# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: zasvid
'''

import wx

import wx.lib.scrolledpanel
from utils import get_wx_image

class ShapePanel(wx.Panel):
    def __init__(self, parent, shape):
        wx.Panel.__init__(self, parent)
        self.shape = shape
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        shapeImage = wx.StaticBitmap(self, -1, get_wx_image(self.shape.get_image()))
        sizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.SetSizer(sizer)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    def OnClick(self, event):
        self.parent.data.current_shape = self.shape
        if self.parent.currently_selected_subpanel is not None:
            self.parent.currently_selected_subpanel.deselect()
        self.parent.currently_selected_subpanel = self 
        self.select()
        self.parent.target_panel.regenerate()

    def deselect(self):
        self.SetBackgroundColour(wx.NullColor)
        
    def select(self):
        self.SetBackgroundColour('#0000ff')


class HierarchyPanel(wx.lib.scrolledpanel.ScrolledPanel):
    
    def __init__(self, parent, data, target_panel):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.data = data
        self.target_panel = target_panel
        self.shape_panels = []
        self.prepare_for_new_layout()
        
    def regenerate(self):
        sizer = self.prepare_for_new_layout()
        for panel in self.shape_panels:
            panel.Destroy()
        self.shape_panels = []
        hierarchy = self.data.current_hierarchy.linearise_hierarchy()
        for i in range(len(hierarchy)):
            shapepanel = ShapePanel(self, hierarchy[i])
            sizer.Add(shapepanel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            sizer.AddSpacer(5)
            self.shape_panels.append(shapepanel)
        sizer.AddStretchSpacer()
        self.SetupScrolling(scroll_y = False)
        self.Refresh()
        self.Update()
        """
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.data = data
        self.target_panel = target_panel
        self.currently_selected_subpanel = None
        self.shape_panels = []
        staticbox = wx.StaticBox(self, label = 'Hierarchia kształtów')
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)
        self.grid_sizer = wx.GridSizer(5, 5, hgap=5, vgap=5)
        
        sizer.Add(self.grid_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.SetSizer(sizer)
        
        
    def regenerate(self):
        self.clear()
        for panel in self.shape_panels:
            panel.Destroy()
        self.shape_panels = []
        hierarchy = self.data.current_hierarchy.linearise_hierarchy()
        for i in range(len(hierarchy)):
            shapepanel = ShapePanel(self, hierarchy[i])
            #self.grid_sizer.Add(shapepanel, 0, wx.ALIGN_CENTER)
            #self.grid_sizer.Add(wx.StaticText(self, label = '<'), 0 , wx.ALIGN_CENTER)
            self.shape_panels.append(shapepanel)
        self.grid_sizer.AddMany(self.shape_panels)
        self.SetSizer(self.grid_sizer)
    """    
    
    def prepare_for_new_layout(self):
        self.currently_selected_subpanel = None
        staticbox = wx.StaticBox(self, label = 'Hierarchia kształtów')
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)
        self.SetSizer(sizer, True)
        return sizer

# -*- coding: utf-8 -*-
'''
    Browser of DjVu shapes    
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
from internal.image_conversion import PilImageToWxBitmap

class RootPanel(wx.Panel):
    def __init__(self, shape, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.parent = kwargs['parent']
        self.shape = shape
        sizer = wx.BoxSizer(wx.VERTICAL)
        imagePanel = wx.Panel(self)
        imageSizer = wx.BoxSizer(wx.HORIZONTAL)
        shapeImage = wx.StaticBitmap(imagePanel, -1, PilImageToWxBitmap(self.shape.image))
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
        sizer.Add(info, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(imagePanel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnChooseThisShape)
        shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnChooseThisShape)
        imagePanel.Bind(wx.EVT_LEFT_DOWN, self.OnChooseThisShape)
        
    def OnChooseThisShape(self, event):
        self.select()

    def deselect(self):
        self.SetBackgroundColour(wx.NullColor)
        
    def select(self):
        self.SetBackgroundColour('#00ff00')
        self.parent.data.current_hierarchy = self.shape
        self.parent.data.current_shape = self.shape
        if self.parent.currently_selected_subpanel is not None:
            self.parent.currently_selected_subpanel.deselect()
        self.parent.currently_selected_subpanel = self 
        for panel in self.parent.target_panels:
            panel.regenerate()
        
class RootsPanel(wx.lib.scrolledpanel.ScrolledPanel):
    
    def __init__(self, data, target_panels, sorting_method, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        self.data = data
        self.target_panels = target_panels
        self.sorting_method = sorting_method
        self.root_panels = []
        self.prepare_for_new_layout()
        
    def regenerate(self):
        sizer = self.prepare_for_new_layout()
        for panel in self.root_panels:
            panel.Destroy()
        self.root_panels = []
        for hierarchy_root in self.data.sorted_hierarchies(self.sorting_method):
            panel = RootPanel(parent = self, shape = hierarchy_root)
            self.root_panels.append(panel)
            sizer.Add(panel, 0, wx.ALL | wx.ALIGN_TOP, 5)
            sizer.AddSpacer(5)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer, True)
        #self.SetupScrolling(scroll_y = False)
        self.SetupScrolling()
        self.Refresh()
        self.Update()
    
    def prepare_for_new_layout(self):
        self.currently_selected_subpanel = None
        static_label = 'Korzenie hierarchii kształtów'
        if self.sorting_method is None:
            static_label += " (nieposortowane)"
        elif self.sorting_method == 'size':
            static_label += " od największego kształtu do najmniejszego"
        elif self.sorting_method == 'count':
            static_label += " od najliczniejszej hierarchii do najmniej licznych"
        staticbox = wx.StaticBox(self, label = static_label)
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)
        self.SetSizer(sizer, True)
        return sizer

    def select(self, shape):
        for panel in self.root_panels:
            if panel.shape.db_id == shape.db_id:
                panel.select()
                break
    
    
    
    def set_hierarchy_sorting_method(self, sorting_method = None):
        if (sorting_method != self.sorting_method):
            self.sorting_method = sorting_method
            self.regenerate()    


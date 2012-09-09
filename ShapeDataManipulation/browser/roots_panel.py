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
from internal.frame import __SCRIPT_PATH__
import os

class RootPanel(wx.Panel):
    def __init__(self, shape, main_widget, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.roots_widget = main_widget
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
        self.width = max(info.GetSize()[0],imagePanel.GetSize()[0]) + 10 
        
    def OnChooseThisShape(self, event):
        self.select()

    def deselect(self):
        self.SetBackgroundColour(wx.NullColor)
        
    def select(self):
        self.SetBackgroundColour('#00ff00')
        self.roots_widget.data.current_hierarchy = self.shape
        self.roots_widget.data.current_shape = self.shape
        if self.roots_widget.currently_selected_subpanel is not None:
            self.roots_widget.currently_selected_subpanel.deselect()
        self.roots_widget.currently_selected_subpanel = self 
        for panel in self.roots_widget.target_panels:
            panel.regenerate()
       
#class RootsPanel(wx.lib.scrolledpanel.ScrolledPanel):
class RootsPanel(wx.Panel):
    
    def __init__(self, data, target_panels, sorting_method, *args, **kwargs):
        #wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        wx.Panel.__init__(self, *args, **kwargs)
        self.data = data
        self.target_panels = target_panels
        self.sorting_method = sorting_method
        self.root_panels = []
        static_label = 'Korzenie hierarchii kształtów'
        if self.sorting_method is None:
            static_label += " (nieposortowane)"
        elif self.sorting_method == 'size':
            static_label += " od największego kształtu do najmniejszego"
        elif self.sorting_method == 'count':
            static_label += " od najliczniejszej hierarchii do najmniej licznych"
        staticbox = wx.StaticBox(self, label = static_label)
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)

        self.buttons = {}
        self._bindings = {'next' : self.next_root,
                          'nextscr': self.next_scroll_roots,
                          'end': self.last_root,
                          'prev': self.prev_root,
                          'prevscr': self.prev_scroll_roots,
                          'home': self.first_root}
        self._button_tooltips = {'next' : u'Pokaż następną hierarchię.',
                          'nextscr': u'Przewiń hierarchie tak, by pierwszą widoczną była następna po obecnie wyświetlanych.',
                          'end': u'Pokaż ostatnią hierarchię.',
                          'prev': u'Pokaż poprzednią hierarchię.',
                          'prevscr': u'Przewiń hierarchie tak, by ostatnią widoczną była poprzednia przed obecnie wyświetlanymi.',
                          'home': u'Pokaż pierwszą hierarchię.'}
        for button_name in ['next', 'nextscr', 'end', 'prev', 'prevscr', 'home']:
            
            image_path = os.path.join(__SCRIPT_PATH__, "resource", button_name + '.png')            
            image = wx.Image(image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.buttons[button_name] = wx.BitmapButton(self, bitmap = image,
                             size = (image.GetWidth()+10, image.GetHeight()))

            tooltip = wx.ToolTip(self._button_tooltips[button_name])
            self.buttons[button_name].SetToolTip(tooltip)
            self.buttons[button_name].Bind(wx.EVT_BUTTON, self._bindings[button_name])
        for button_name in ['home', 'prevscr', 'prev']:
            sizer.Add(self.buttons[button_name], 0, wx.ALIGN_CENTER | wx.EXPAND) 
        self.inner = wx.lib.scrolledpanel.ScrolledPanel(self)
        sizer.Add(self.inner, 1, wx.EXPAND | wx.ALL, 1)
        for button_name in ['next', 'nextscr', 'end']:
            sizer.Add(self.buttons[button_name], 0, wx.ALIGN_CENTER | wx.EXPAND)

        self.SetSizer(sizer, True)
        self.currently_selected_subpanel = None

        
    def next_root(self, event):
        index = min(self.max_index, self.visible_index + 1)
        self.compute_root_visibility(self.visible_index+1)

    def next_scroll_roots(self, event):
        index = min(self.max_index, self.visible_index + len(self.visible_panels))
        self.compute_root_visibility(index)

    def prev_root(self, event):
        index = max(0, self.visible_index - 1)
        self.compute_root_visibility(index)

    def prev_scroll_roots(self, event):
        index = max(0, self.visible_index - len(self.visible_panels))
        self.compute_root_visibility(index)

    def last_root(self, event):
        self.compute_root_visibility(self.max_index)
        
    def first_root(self, event):
        self.compute_root_visibility(0)
        
    def compute_root_visibility(self, index):
        inner_width = self.inner.GetSize()[0]
        visible_panels_width = 0
        for panel in self.visible_panels:
            panel.Hide()
        self.visible_panels = []
        for root_panel in self.root_panels[index:]:
            root_panel.Show()
            visible_panels_width += root_panel.width
            self.visible_panels.append(root_panel)
            if visible_panels_width >= inner_width:
                break
        self.visible_index = index
        self.inner.Layout()
        self.inner.Refresh()
        self.inner.Update()
    
    def regenerate(self):
        self.currently_selected_subpanel = None
        self.visible_index = 0
        self.max_index = len(self.data.sorted_hierarchies(self.sorting_method)) - 1
        self.inner_sizer = sizer = wx.BoxSizer(wx.HORIZONTAL)
        for panel in self.root_panels:
            panel.Destroy()
        
        self.root_panels = []
        self.visible_panels = []
        for hierarchy_root in self.data.sorted_hierarchies(self.sorting_method):
            panel = RootPanel(parent = self.inner, shape = hierarchy_root, main_widget = self)
            self.root_panels.append(panel)
            sizer.Add(panel, 0, wx.ALIGN_TOP | wx.EXPAND)
            panel.Hide()
        sizer.AddStretchSpacer()
        self.inner.SetSizer(sizer, True)
        self.inner.SetupScrolling(scroll_x = False)
        self.compute_root_visibility(self.visible_index)

    def select(self, shape):
        for panel in self.root_panels:
            if panel.shape.db_id == shape.db_id:
                panel.select()
                break
    
    def set_hierarchy_sorting_method(self, sorting_method = None):
        if (sorting_method != self.sorting_method):
            self.sorting_method = sorting_method
            self.regenerate()    

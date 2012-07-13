# -*- coding: utf-8 -*-
'''
    DjVu Shape Tools  
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


import wx.lib.scrolledpanel
from internal.image_conversion import PilImageToWxBitmap   

_SHAPE_IMAGE_MARGIN = 5

_s = {'Title' : u'Hierarchia kształtów',
      'VertexDepth' : u"Poziom węzła: ",
      'SubtreeCount': u"Wielkość poddrzewa: ",
      'SubtreeHeight': u"Wysokość poddrzewa: ",
      'BlitCount' : u"Ilość wystąpień w dokumencie: ",
      'CutShapeOut': u"Wytnij kształt z hierarchii",
      'CutShapeOff': u"Odetnij poddrzewo od hierarchii"
}

def childrenOf(shapes):
    children = []
    for shape in shapes:
        children.extend(shape.children)
    return children

def grade_color(part, full):
    min_grade = 40
    max_grade = 255
    color_int = (max_grade - min_grade)*part / full + min_grade
    return hex(color_int)[2:]


class _ShapePanel(wx.Panel):
    def __init__(self, shape, shapes_panel, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.shape = shape
        self.shapes_panel = shapes_panel
        self.SetMinSize(kwargs['size'])
        
        shapeImage = wx.StaticBitmap(self, -1, PilImageToWxBitmap(self.shape.image))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, _SHAPE_IMAGE_MARGIN)
        self.SetSizer(sizer)        
                
        tooltip_text = _s['VertexDepth'] + str(shape.hierarchy_depth()+1)
        tooltip_text += u'\n' + _s['SubtreeCount'] + str(shape.count_descendants()) 
        tooltip_text += u'\n' + _s['SubtreeHeight'] + str(shape.hierarchy_height())
        if self.shapes_panel.data.blits:
            tooltip_text += u'\n' + _s['BlitCount'] + str(shape.blit_count)
        tooltip = wx.ToolTip(tooltip_text) 
        self.SetToolTip(tooltip)
        shapeImage.SetToolTip(tooltip)
        self._image = shapeImage
        if not self.shapes_panel.labelling:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnChooseThisShape)
            shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnChooseThisShape)
        if self.shapes_panel.labelling:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnPopup)
            shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnPopup)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnPopup)
        shapeImage.Bind(wx.EVT_RIGHT_DOWN, self.OnPopup)
        self._cut_regenerate = False    
        self._has_special_colour = False

    def Dispose(self):
        #self.SetToolTip(None)
        #self._image.SetToolTip(None)
        self.Hide()

    def OnChooseThisShape(self, event):
        self.shapes_panel.data.current_shape = self.shape
        if self.shapes_panel.target_panel is not None: 
            self.shapes_panel.target_panel.regenerate()
        self.select()

    def OnPopup(self, event):
        self.highlight_cut_head()
        self.shapes_panel.highlight_cut_descendants(self.shape)
        menu = wx.Menu()
        item = menu.Append(id = wx.ID_ANY, text = _s['CutShapeOut'])
        self.Bind(wx.EVT_MENU, self.OnCutOut, item)
        item = menu.Append(id = wx.ID_ANY, text = _s['CutShapeOff'])
        self.Bind(wx.EVT_MENU, self.OnCutOff, item)
        self.PopupMenu(menu)
        menu.Destroy()
        if self._cut_regenerate:
            for callback in self.shapes_panel.callbacks:
                callback.regenerate()
            self.shapes_panel.regenerate()
            self._cut_regenerate = False
        else: # restore cut_highlighted_panels
            for panel, color in self.shapes_panel.cut_highlighted_panels:
                if color is None:
                    panel.deselect()
                else:
                    panel.SetBackgroundColour(color)
            self.shapes_panel.cut_highlighted_panels = []

    def OnCutOut(self, event):
        self.shapes_panel.data.cut_out(self.shape)
        self._cut_regenerate = True
        
    def OnCutOff(self, event):
        self.shapes_panel.data.cut_off(self.shape)
        self._cut_regenerate = True

    def highlight_cut_head(self):
        if self._has_special_color:
            bg_color = self.GetBackgroundColour()
        else:
            bg_color = None
        self.shapes_panel.cut_highlighted_panels.append((self, bg_color))
        self.SetBackgroundColour('#ffff00')
        self._has_special_color = True
        
    def highlight_cut_descendant(self):
        if self._has_special_color:
            bg_color = self.GetBackgroundColour()
        else:
            bg_color = None
        self.shapes_panel.cut_highlighted_panels.append((self, bg_color))
        self.SetBackgroundColour('#ffa500')
        self._has_special_color = True

    def deselect(self):
        self.SetBackgroundColour(wx.NullColor)
        self._has_special_color = False
        #print(str(self.shape) + " has been deselected!")
        
    def select(self):
        if self.shapes_panel._currently_selected_subpanel is not None:
            self.shapes_panel._currently_selected_subpanel.deselect()
        self.shapes_panel._currently_selected_subpanel = self
        for shape_panel in self.shapes_panel.highlighted_panels:
            shape_panel.deselect()
        self.shapes_panel.highlighted_panels = []
        self.SetBackgroundColour('#0000ff')
        self._has_special_color = True
        self.shapes_panel.highlight_branch(self.shape)

    def highlightAncestor(self, ancestor_depth, max_depth):
        self.SetBackgroundColour('#' + grade_color(ancestor_depth, max_depth) + '0000')
        self._has_special_color = True

    def highlightDescendant(self, difference, max_depth):
        
        self.SetBackgroundColour('#00' + grade_color(max_depth - difference, max_depth) + '00')
        self._has_special_color = True


class ShapesPanel(wx.Panel):
    def __init__(self, data, target_panel = None, labelling = False, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.data = data
        self.target_panel = target_panel
        self.labelling = labelling
        
        self.callbacks = []
        self.shape_panels = []
        self.highlighted_panels = []
        self.cut_highlighted_panels = []
        
        self.panel = wx.lib.scrolledpanel.ScrolledPanel(self)
        staticbox = wx.StaticBox(self, label = _s['Title'])
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)
        sizer.Add(self.panel, 1, wx.ALL | wx.EXPAND,1)
        self.SetSizer(sizer)
        self.panel.SetupScrolling()
                
    def regenerate(self):
        previous_shape_panels = self.shape_panels
        sizer = wx.GridSizer()
        labelling_panel = None
        
        self._currently_selected_subpanel = None
        self.shape_panels = []
        self.highlighted_panels = []
        self.cut_highlighted_panels = []
        
        
        if self.data.current_hierarchy is not None:
            max_shape_width, max_shape_height = self.data.current_hierarchy.get_hierarchy_size()
            shape_panel_size = (max_shape_width + 2 * _SHAPE_IMAGE_MARGIN, max_shape_height + 2*_SHAPE_IMAGE_MARGIN)
            panel_width, _ = self.panel.GetSize()
            columns = panel_width / (max_shape_width + 2 * _SHAPE_IMAGE_MARGIN) 
            sizer.SetCols(columns)
            hierarchy = self.data.current_hierarchy.linearise_hierarchy()
            for shape in hierarchy:
                shapepanel = _ShapePanel(parent = self.panel, shape = shape, shapes_panel = self, size = shape_panel_size)
                #if self.labelling and self.data.current_shape == shape:
                #   labelling_panel = shapepanel
                sizer.Add(shapepanel)
                self.shape_panels.append(shapepanel)
            #if self.labelling:
            #   labelling_panel.select()
        self.panel.SetSizer(sizer)
        self.panel.Layout()
        for panel in previous_shape_panels:
            panel.Dispose()
            
    def highlight_cut_descendants(self, shape):
        for shape_panel in self.shape_panels:
            if shape_panel.shape.isDescendantOf(shape):
                shape_panel.highlight_cut_descendant()
                
    def highlight_branch(self, shape):
        for shape_panel in self.shape_panels:
            if shape_panel.shape.isAncestorOf(shape):
                shape_panel.highlightAncestor(shape_panel.shape.hierarchy_depth(), shape.hierarchy_depth())
                self.highlighted_panels.append(shape_panel)
            elif shape_panel.shape.isDescendantOf(shape):
                shape_panel.highlightDescendant(shape_panel.shape.hierarchy_depth() - shape.hierarchy_depth(), shape.hierarchy_height())
                self.highlighted_panels.append(shape_panel)
        
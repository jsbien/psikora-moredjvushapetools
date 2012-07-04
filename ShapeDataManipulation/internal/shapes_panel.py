# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: zasvid
'''

import wx
import wx.lib.scrolledpanel
from internal.image_conversion import PilImageToWxBitmap   

shape_image_margin = 5

def childrenOf(shapes):
    children = []
    for shape in shapes:
        children.extend(shape.children)
    return children

def grade_color(part, full):
    min_grade = 10
    max_grade = 255
    color_int = (max_grade - min_grade)*part / full + min_grade
    return hex(color_int)[2:]

class _ShapePanel(wx.Panel):
    def __init__(self, shape, shapes_panel, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.shape = shape
        self.shapes_panel = shapes_panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        #shapeImage = wx.StaticBitmap(self, -1, Pil(self.shape.get_image()))
        shapeImage = wx.StaticBitmap(self, -1, PilImageToWxBitmap(self.shape.get_image()))
        sizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, shape_image_margin)
        
        tooltip_text = "Poziom węzła: " + str(shape.hierarchy_depth()+1) + '\n'
        #tooltip_text += "Gałąź drzewa: " + str(0) + '\n'
        tooltip_text += "Wielkość poddrzewa: " + str(shape.count_descendants()) + '\n'
        tooltip_text += "Wysokość poddrzewa: " + str(shape.hierarchy_height())
        self._has_special_color = False
        
        tooltip = wx.ToolTip(tooltip_text) 
        
        self.SetSizer(sizer)
        if not self.shapes_panel.labelling:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnChooseThisShape)
            shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnChooseThisShape)
        self.SetToolTip(tooltip)
        shapeImage.SetToolTip(tooltip)
        
        if self.shapes_panel.labelling:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnPopup)
            shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnPopup)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnPopup)
        shapeImage.Bind(wx.EVT_RIGHT_DOWN, self.OnPopup)
        self.cut_regenerate = False
        
    def OnChooseThisShape(self, event):
        self.shapes_panel.data.current_shape = self.shape
        if self.shapes_panel.target_panel is not None: 
            self.shapes_panel.target_panel.regenerate()
        self.select()

    def OnPopup(self, event):
        self.highlight_cut_head()
        self.shapes_panel.highlight_cut_descendants(self.shape)
        menu = wx.Menu()
        item = menu.Append(id = wx.ID_ANY, text = "Wytnij kształt z hierarchii")
        self.Bind(wx.EVT_MENU, self.OnCutOut, item)
        item = menu.Append(id = wx.ID_ANY, text = "Odetnij poddrzewo od hierarchii")
        self.Bind(wx.EVT_MENU, self.OnCutOff, item)
        self.PopupMenu(menu)
        menu.Destroy()
        if self.cut_regenerate:
            for callback in self.shapes_panel.callbacks:
                callback.regenerate()
            self.shapes_panel.regenerate()
            self.cut_regenerate = False
        else: # restore cut_highlighted_panels
            for panel, color in self.shapes_panel.cut_highlighted_panels:
                if color is None:
                    panel.deselect()
                else:
                    panel.SetBackgroundColour(color)
            self.shapes_panel.cut_highlighted_panels = []

    def OnCutOut(self, event):
        self.shapes_panel.data.cut_out(self.shape)
        self.cut_regenerate = True
        
    def OnCutOff(self, event):
        self.shapes_panel.data.cut_off(self.shape)
        self.cut_regenerate = True
            
    def deselect(self):
        self.SetBackgroundColour(wx.NullColor)
        self._has_special_color = False
        #print(str(self.shape) + " has been deselected!")
        
        
    def select(self):
        if self.shapes_panel.currently_selected_subpanel is not None:
            self.shapes_panel.currently_selected_subpanel.deselect()
        self.shapes_panel.currently_selected_subpanel = self
        for shape_panel in self.shapes_panel.highlighted_panels:
            shape_panel.deselect()
        self.shapes_panel.highlighted_panels = []
        self.SetBackgroundColour('#0000ff')
        self._has_special_color = True
        self.shapes_panel.highlight_branch(self.shape)
        
        
    def highlight_cut_head(self):
        if self._has_special_color:
            bg_color = self.GetBackgroundColour()
        else:
            bg_color = None
        self.shapes_panel.cut_highlighted_panels.append((self, bg_color))
        self.SetBackgroundColour('#ffff00')
#        self._has_special_color = True
        
    def highlight_cut_descendant(self):
        if self._has_special_color:
            bg_color = self.GetBackgroundColour()
        else:
            bg_color = None
        self.shapes_panel.cut_highlighted_panels.append((self, bg_color))
        self.SetBackgroundColour('#ffa500')
 #       self._has_special_color = True

    def highlightAncestor(self, ancestor_depth, max_depth):
        self.SetBackgroundColour('#' + grade_color(ancestor_depth, max_depth) + '0000')
        self._has_special_color = True

    def highlightDescendant(self, difference, max_depth):
        #print(str(self.shape.db_id) + " has been highlighted as a descendant!")
        self.SetBackgroundColour('#00' + grade_color(max_depth - difference, max_depth) + '00')
        self._has_special_color = True

class ShapesPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, data, target_panel = None, labelling = False, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        self.data = data
        self.target_panel = target_panel
        self.labelling = labelling
        self.shape_panels = []
        self.highlighted_panels = []
        self.cut_highlighted_panels = []
        self.panel = wx.Panel(self)
        staticbox = wx.StaticBox(self, label = 'Hierarchia kształtów')
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)
        sizer.Add(self.panel, 1, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(sizer)
        self.callbacks = []
        self._grid_sizer = None
        
    def regenerate(self):
        self.currently_selected_subpanel = None

        for shape_panel in self.shape_panels:
            shape_panel.Hide()
            
        self.shape_panels = []
        self.highlighted_panels = []
        self.cut_highlighted_panels = []
        
        labelling_panel = None

        if self.data.current_hierarchy is not None:
            max_shape_width, max_shape_height = self.data.current_hierarchy.get_hierarchy_size()
            shape_panel_size = (max_shape_width + 2*shape_image_margin, max_shape_height + 2*shape_image_margin)
            panel_width, _ = self.panel.GetSize()
            columns = panel_width / (max_shape_width + 2*shape_image_margin) 
            sizer = wx.GridBagSizer()
            hierarchy = self.data.current_hierarchy.linearise_hierarchy()
            pos_col, pos_row = (1,1)
            for i in range(len(hierarchy)):
                shapepanel = _ShapePanel(parent = self.panel, shapes_panel = self, shape = hierarchy[i], size = shape_panel_size)
                if self.labelling and self.data.current_shape == hierarchy[i]:
                    labelling_panel = shapepanel
                sizer.Add(shapepanel, (pos_row, pos_col))
                pos_col += 1
                if pos_col > columns:
                    pos_col = 1
                    pos_row += 1 
                self.shape_panels.append(shapepanel)

            self.panel.SetSizer(sizer)
            self._grid_sizer = sizer
            if self.labelling:
                labelling_panel.select()
            self.SetupScrolling()
            self.Refresh()
            self.Update()
    
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
        self.Refresh()
        self.Update()
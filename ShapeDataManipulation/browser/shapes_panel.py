# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: zasvid
'''

import wx
import wx.lib.scrolledpanel
from internal.image_conversion import PilImageToWxBitmap   

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
    def __init__(self, shape, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.shape = shape
        self.parent = kwargs['parent']
        sizer = wx.BoxSizer(wx.VERTICAL)
        #shapeImage = wx.StaticBitmap(self, -1, Pil(self.shape.get_image()))
        shapeImage = wx.StaticBitmap(self, -1, PilImageToWxBitmap(self.shape.get_image()))
        sizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.SetSizer(sizer)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        shapeImage.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    def OnClick(self, event):
        self.parent.data.current_shape = self.shape
        if self.parent.currently_selected_subpanel is not None:
            self.parent.currently_selected_subpanel.deselect()
        self.parent.currently_selected_subpanel = self 
        self.parent.target_panel.regenerate()
        for shape_panel in self.parent.highlighted_panels:
            shape_panel.deselect()
        self.parent.highlighted_panels = []
        self.parent.highlight_branch(self.shape)
        self.select()


    def deselect(self):
        self.SetBackgroundColour(wx.NullColor)
        
    def select(self):
        self.SetBackgroundColour('#0000ff')

    def highlightAncestor(self, ancestor_depth, max_depth):
        self.SetBackgroundColour('#' + grade_color(ancestor_depth, max_depth) + '0000')

    def highlightDescendant(self, difference, max_depth):
        self.SetBackgroundColour('#00' + grade_color(difference, max_depth) + '00')


class ShapesPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, data, target_panel, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        self.data = data
        self.target_panel = target_panel
        self.shape_panels = []
        self.highlighted_panels = []
        self.panel = wx.Panel(self)
        staticbox = wx.StaticBox(self, label = 'Hierarchia kształtów')
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.HORIZONTAL)
        sizer.Add(self.panel, 1, wx.ALL | wx.EXPAND, 15)
        self.SetSizer(sizer)
        
    def regenerate(self):
        self.currently_selected_subpanel = None
        #self.panel.DestroyChildren()
        for panel in self.shape_panels:
            panel.Destroy()
        self.shape_panels = []
        self.highlighted_panels = []
        if self.data.current_hierarchy is not None:
            max_shape_width, max_shape_height = self.data.current_hierarchy.get_hierarchy_size()
            shape_panel_size = (max_shape_width + 5, max_shape_height + 5)
            panel_width, _ = self.panel.GetSize()
            columns = panel_width / max_shape_width
            sizer = wx.GridBagSizer()
            hierarchy = self.data.current_hierarchy.linearise_hierarchy()
            pos_col, pos_row = (1,1)
            for i in range(len(hierarchy)):
                shapepanel = _ShapePanel(parent = self, shape = hierarchy[i], size = shape_panel_size)
                sizer.Add(shapepanel, (pos_row, pos_col))
                pos_col += 1
                if pos_col > columns:
                    pos_col = 1
                    pos_row += 1 
                self.shape_panels.append(shapepanel)
            self.panel.SetSizer(sizer)
            self.SetupScrolling(scroll_y = False)
            self.Refresh()
            self.Update()
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if self.data.current_hierarchy is not None:
            hierarchy = self.data.current_hierarchy.linearise_hierarchy()
            for i in range(len(hierarchy)):
                shapepanel = _ShapePanel(parent = self, shape = hierarchy[i])
                sizer.Add(shapepanel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
                sizer.AddSpacer(5)
                self.shape_panels.append(shapepanel)
            sizer.AddStretchSpacer()
            self.panel.SetSizer(sizer)
            self.SetupScrolling(scroll_y = False)
            self.Refresh()
            self.Update()
        """
        
    
    def highlight_branch(self, shape):
        
        for shape_panel in self.shape_panels:
            if shape_panel.shape.isAncestorOf(shape):
                shape_panel.highlightAncestor(shape_panel.shape.hierarchyheight(), shape.hierarchyheight())
                self.highlighted_panels.append(shape_panel)
            elif shape_panel.shape.isDescendantOf(shape):
                shape_panel.highlightDescendant(shape_panel.shape.hierarchyheight() - shape.hierarchyheight(), shape.depth())
                self.highlighted_panels.append(shape_panel)
        

"""
class HierarchyPanel(wx.lib.scrolledpanel.ScrolledPanel):
    
    def __init__(self, data, target_panel, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        self.data = data
        self.target_panel = target_panel
        self.shape_panels = []
        self.prepare_for_new_layout()
    
    def OnCellClick(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if (row,col) in self.shape_positions:
            self.data.current_shape = self.shape_position[(row,col)]
            self.target_panel.regenerate()
    
    def regenerate(self):
        sizer = wx.BoxSizer()
        if self.grid is not None:
            self.grid.Destroy()
        self.grid = wx.grid.Grid(self)
        self.shape_positions = {}
        
        hierarchy = self.data.current_hierarchy.linearise_hierarchy()
        max_depth = 0
        for shape in hierarchy:
            if shape.depth() > max_depth:
                max_depth = shape.depth()
        max_width = self.data.current_hierarchy.max_width()
        grid_rows, grid_cols = max_width, 2*max_depth - 1 
        self.grid.CreateGrid(grid_rows, grid_cols)
        self.grid.EnableDragGridSize(False)
        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)
        
        
        depth = 1
        next_shapes = [self.data.current_hierarchy]
        while depth <= grid_cols:
            shapes = next_shapes
            next_shapes = childrenOf(shapes)
            for i in range(1,len(shapes)+1):
                imageRenderer = MyImageRenderer(shapes[i-1])
                self.grid.SetCellRenderer(i,depth,imageRenderer)
                self.grid.SetColSize(depth,shapes[i-1].GetWidth()+2)
                self.grid.SetRowSize(i, shapes[i-1].GetHeight()+2)
            depth += 1
            if depth < grid_cols:
                for i in range (1, grid_rows + 1):
                    imageRenderer = MyImageRenderer(self.arrows['left'])
                    self.grid.SetCellRenderer(i,depth,imageRenderer)
                    print(str(i) + ',' + str(depth))
                    self.grid.SetColSize(depth,self.arrows['left'].GetWidth()+2)
                    self.grid.SetRowSize(i, self.arrows['left'].GetHeight()+2)
            
                    depth += 1
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
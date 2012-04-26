# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: zasvid
'''

import wx

import wx.grid
from os import sep
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


def childrenOf(shapes):
    children = []
    for shape in shapes:
        children.extend(shape.children)
    return children

class HierarchyPanel(wx.lib.scrolledpanel.ScrolledPanel):
    
    def __init__(self, parent, data, target_panel):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.data = data
        self.target_panel = target_panel
        self.shape_panels = []
        self.prepare_for_new_layout()
        self.grid = None
        self.arrows = {'up': wx.Bitmap("data" + sep + "arrow_up.png", wx.BITMAP_TYPE_PNG),
                       'down': wx.Bitmap("data" + sep + "arrow_down.png", wx.BITMAP_TYPE_PNG),
                       'left': wx.Bitmap("data" + sep + "arrow_left.png", wx.BITMAP_TYPE_PNG),
                       'right': wx.Bitmap("data" + sep + "arrow_right.png", wx.BITMAP_TYPE_PNG)}
    
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
        """
        shape_rows = {}
        shape_cols = {}
        shapes = [self.data.current_hierarchy]
        depth = 1
        while depth < grid_height:
            for shape in shapes:
                shape_cols[depth] = shape
        """
        
        '''
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellClick)
        #self.grid.AutoSize()
        sizer.Add(self.grid, 1, wx.ALL, 5)
        self.SetSizer(sizer)
        self.Layout()
        self.SetupScrolling()
        self.Refresh()
        self.Update()
        
        '''
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
        '''
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

class MyImageRenderer(wx.grid.PyGridCellRenderer):
        def __init__(self, img):
            wx.grid.PyGridCellRenderer.__init__(self)
            self.img = img

        def Draw(self, grid, attr, dc, rect, row, col, isSelected):
            image = wx.MemoryDC()
            image.SelectObject(self.img)
            dc.SetBackgroundMode(wx.SOLID)
            if isSelected:
                dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
                dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
            else:
                dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
                dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
            dc.DrawRectangleRect(rect)
            width, height = self.img.GetWidth(), self.img.GetHeight()
            if width > rect.width-2:
                width = rect.width-2
            if height > rect.height-2:
                height = rect.height-2
            dc.Blit(rect.x+1, rect.y+1, width, height, image, 0, 0, wx.COPY, True)


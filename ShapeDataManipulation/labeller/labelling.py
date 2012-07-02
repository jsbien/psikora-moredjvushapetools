'''
Created on Jun 3, 2012

@author: zasvid
'''

import wx
from internal.label_panel import LabelPanel
from internal.shapes_panel import ShapesPanel

class LabellingPanel(wx.Panel):
    
    def __init__(self, data, data_hocr, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.data = data
        self.data_hocr = data_hocr
        
        sizer = wx.BoxSizer(orient = wx.VERTICAL)
        panel = wx.Panel(self)
        sizer.Add(panel, 0, wx.EXPAND)
        
        width, _ = self.GetSize()
        self.line_edit = wx.TextCtrl(self, size = (20, width))

        sizer.Add(self.line_edit, 0, wx.EXPAND)
        sizer.AddSpacer((5,5))

        label_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)        
        self.label = LabelPanel(parent = self, labelling = True, data = self.data)
        
        self.shapes = ShapesPanel(parent = self, labelling = True, data = self.data, target_panel = None)
        
        label_sizer.Add(self.label, 1, wx.ALL | wx.EXPAND, 5)
        label_sizer.Add(self.shapes, 1, wx.ALL | wx.EXPAND, 5)
                
        sizer.Add(label_sizer, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        
    def regenerate(self):
        self.line_edit.ChangeValue(self.data_hocr.get_line_text())
        sel_from, sel_to = self.data_hocr.text_model.get_current_char_position() 
        self.line_edit.SetSelection(sel_from, sel_to)
        self.line_edit.SetFocus()
        self.label.regenerate()
        #self.shapes.regenerate()
    
    def get_selected_character(self):
        return self.line_edit.GetStringSelection()   
    
    def save_label(self):
        unicode_character = self.get_selected_character()
        self.label.save_label(unicode_character)
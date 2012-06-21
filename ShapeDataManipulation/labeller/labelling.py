'''
Created on Jun 3, 2012

@author: zasvid
'''

import wx
from internal.label_panel import LabelPanel

class LabellingPanel(wx.Panel):
    
    def __init__(self, data, data_hocr, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.data = data
        self.data_hocr = data_hocr
        
        sizer = wx.BoxSizer(orient = wx.VERTICAL)
        width, _ = self.GetSize()
        self.line_edit = wx.TextCtrl(self, size = (20, width))
        
        sizer.Add(self.line_edit, 0, wx.EXPAND)
        sizer.AddSpacer((5,5))
        
        self.label = LabelPanel(parent = self, data = self.data)
        
        sizer.Add(self.label, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        
    def regenerate(self):
        self.line_edit.ChangeValue(self.data_hocr.get_line_text())
        self.line_edit.SelectAll()
        self.label.regenerate()
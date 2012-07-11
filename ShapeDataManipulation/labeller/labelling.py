# -*- coding: utf-8 -*-
'''
    hOCR Labeller of DjVu shapes    
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
from internal.label_panel import LabelPanel
from internal.shapes_panel import ShapesPanel
from labeller.line_preview import LinePreviewPanel

class LabellingPanel(wx.Panel):
    
    def __init__(self, data, data_hocr, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._dirty_label = False
        self.dirty_hocr = {}
        self.data = data
        self.data_hocr = data_hocr
        
        sizer = wx.BoxSizer(orient = wx.VERTICAL)
        self.line_preview_panel = LinePreviewPanel(parent = self)
        sizer.Add(self.line_preview_panel, flag = wx.EXPAND)
        sizer.AddSpacer((3,3))
        width, _ = self.GetSize()
        self.line_edit = wx.TextCtrl(self, size = (20, width))

        sizer.Add(self.line_edit, flag = wx.EXPAND)
        sizer.AddSpacer((3,3))

        label_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)        
        self.label = LabelPanel(parent = self, labelling = True, data = self.data)
        
        self.shapes = ShapesPanel(parent = self, labelling = True, data = self.data, target_panel = None)
        
        label_sizer.Add(self.label, 1, wx.ALL | wx.EXPAND, 5)
        label_sizer.Add(self.shapes, 1, wx.ALL | wx.EXPAND, 5)
                
        sizer.Add(label_sizer, 1, flag =  wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        
        self.line_edit.Bind(wx.EVT_TEXT, self.OnTextChange)
        
    def OnTextChange(self, event):
        text = self.get_selected_character()
        if len(text) > 0:
            self.label.regenerate(text)
        self._dirty_label = True
        
    def regenerate(self):
        #self.line_edit.ChangeValue(self.data_hocr.get_line_text())
        self._dirty_label = False
        self.line_edit.ChangeValue(self.data_hocr.text_model.get_char_text())
        self.line_edit.SetFocus()
        self.line_preview_panel.generate_preview(self.data_hocr.get_line_rect(), self.data_hocr.get_line_blits(), self.data_hocr.get_char_rect())
        self.label.regenerate(self.get_selected_character())
        self.shapes.regenerate()
        self.Layout()
        self.Refresh()
        self.Update()
    
    def get_selected_character(self):
        #sel_from, sel_to = self.data_hocr.text_model.get_current_char_position() 
        #self.line_edit.SetSelection(sel_from, sel_to)
        #return self.line_edit.GetStringSelection()
        return self.line_edit.GetValue()
    
    def save_label(self):
        characters = self.get_selected_character()
        if self._dirty_label:
            if len(characters) > 1:
                #multiply character nodes
                pass
            elif len(characters) < 0:
                #delete node
                pass
            else: #only 1 character
                self.data_hocr.text_model.current_char_node.text = characters
                self.dirty_hocr[self.data_hocr.text_model.current_page] = True
        if len(characters) == 1:
            self.label.save_label(characters)
        
    def OnNextLine(self, event):
        self.data_hocr.text_model.next_line()
        self.regenerate()
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

import wx


class ChooseDocumentDialog(wx.Dialog):
    
    def __init__(self, data, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)

        self.data = data
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.ListBox(self, wx.ID_ANY)
        selection = 0

        for i in range(len(self.data.documents)):
            self.listbox.Insert(self.data.documents[i].name, i, self.data.documents[i])
            if self.data.current_document == self.data.documents[i]:
                selection = i
        
        self.listbox.Select(selection)
        self.listbox.SetFocus()
        
        
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.StdDialogButtonSizer()
        
        okButton = wx.Button(self, id = wx.ID_OK, label='Ok')
        cancelButton = wx.Button(self, id = wx.ID_CANCEL, label='Anuluj')
        
        okButton.Bind(wx.EVT_BUTTON, self.OnChoice)
        okButton.SetDefault()
        cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)
        
        button_sizer.SetAffirmativeButton(okButton)
        button_sizer.SetCancelButton(cancelButton)
        button_sizer.Realize()
        sizer.Add(button_sizer, 1, flag= wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        self.SetSizer(sizer)
        
    def OnChoice(self, event):
        if self.listbox.GetSelection()!=-1:
            self.data.current_document = self.data.documents[self.listbox.GetSelection()]
        self.Close()
    
    def OnClose(self, event):
        self.Close()



class ChooseDictionaryDialog(wx.Dialog):
    
    def __init__(self, data, *args, **kwargs):
        
        wx.Dialog.__init__(self, *args, **kwargs)

        self.data = data
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.ListBox(self, wx.ID_ANY)

        selection = 0
        
        for i in range(len(self.data.shape_dictionaries)):
            self.listbox.Insert(self.data.shape_dictionaries[i].name, i, self.data.shape_dictionaries[i])
            if self.data.current_dictionary == self.data.shape_dictionaries[i]:
                selection = i
        
        self.listbox.Select(selection)
        self.listbox.SetFocus()

        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.StdDialogButtonSizer()
        
        okButton = wx.Button(self, id = wx.ID_OK, label='Ok')
        cancelButton = wx.Button(self, id = wx.ID_CANCEL, label='Anuluj')
        
        okButton.Bind(wx.EVT_BUTTON, self.OnChoice)
        okButton.SetDefault()
        cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)
        
        button_sizer.SetAffirmativeButton(okButton)
        button_sizer.SetCancelButton(cancelButton)
        button_sizer.Realize()

        sizer.Add(button_sizer, 1, flag= wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        self.SetSizer(sizer)
        
    def OnChoice(self, event):
        if self.listbox.GetSelection()!=-1:
            self.data.current_dictionary = self.data.shape_dictionaries[self.listbox.GetSelection()]
        self.Close()
    
    def OnClose(self, event):
        self.Close()

class ChooseCutShapeDialog(wx.Dialog):
    
    def __init__(self, shapes_panel, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)
        self._shapes_panel = shapes_panel
        self._shape_panel = None
        self._viable_coords = []
        self._rows = []
        self._cols = []
        for row, col in self._shapes_panel.get_viable_coordinates():
            if row not in self._rows:
                self._rows.append(row)
            if col not in self._cols:
                self._cols.append(col)
            self._viable_coords.append(row+col)
        self._default_coords = ''
        if len(self._viable_coords) == 1:
            self._default_coords = self._viable_coords[0]
        else:
            if len(self._rows) == 1:
                self._default_coords = self._rows[0]
        
        cancelButton = wx.Button(self, id = wx.ID_CANCEL, label='Anuluj')
        self.Bind(wx.EVT_BUTTON, self.OnClose, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.cutoutButton = wx.Button(self, id = wx.ID_ANY, label='&Wytnij kształt')
        self.Bind(wx.EVT_BUTTON, self.OnCutOut, id = self.cutoutButton.GetId())
        self.cutoffButton = wx.Button(self, id = wx.ID_ANY, label='&Odetnij poddrzewo')
        self.Bind(wx.EVT_BUTTON, self.OnCutOff, id = self.cutoffButton.GetId())
        cutoffLabel = wx.StaticText(self, label = "Alt+O by wybrać powyższą akcję")
        cutoutLabel = wx.StaticText(self, label = "Alt+W by wybrać powyższą akcję")
        textctrllabel = wx.StaticText(self, label = "Wpisz współrzędne kształtu:")

#        self.coords_input = wx.ComboBox(self, choices = self.choices, style = wx.CB_SORT | wx.CB_DROPDOWN)
        self.coords_input = wx.TextCtrl(self)
        
        #self.coords_input.Bind(wx.EVT_COMBOBOX, self.OnChoice)
        self.coords_input.Bind(wx.EVT_TEXT, self.EvtText)
        self.coords_input.SetValue(self._default_coords)
        #self.coords_input.Bind(wx.EVT_CHAR, self.EvtChar)
        
        atable = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL)])
        self.SetAcceleratorTable(atable) 

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.Add(textctrllabel, 0, wx.CENTER | wx.TOP, 10)
        sizer.Add(self.coords_input, 0, wx.CENTER | wx.BOTTOM, 15)
        sizer.Add(self.cutoffButton, 0, wx.CENTER)
        sizer.Add(cutoffLabel, 0, wx.CENTER | wx.BOTTOM, 15)
        sizer.Add(self.cutoutButton, 0, wx.CENTER)
        sizer.Add(cutoutLabel, 0, wx.CENTER | wx.BOTTOM, 15)
        sizer.Add(cancelButton, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)

        self.coords_input.SetFocus()
        
    def OnCutOut(self, event):
        self._shape_panel.cut_out()
        self.Close()
        
    def OnCutOff(self, event):    
        self._shape_panel.cut_off()
        self.Close()
        
    def OnClose(self, event):
        if self._shape_panel is not None:
            self._shape_panel.cut_cleanup()
        event.Skip()

    def OnChoice(self, coord_str):
        coords = (coord_str[0], coord_str[1])
        self._shape_panel = self._shapes_panel.get_shape_at(coords)
        self._shape_panel.highlight_cut()
        self.cutoffButton.Enable()
        self.cutoutButton.Enable()

    def EvtText(self, event):
        """ Validate text in combobox """
        currentText = event.GetString()
        first = None
        second = None
        final_text = ''
        if len(currentText) > 0:
            first = currentText[0]
        if len(currentText) > 1:
            second = currentText[1]
        if first in self._rows + self._cols:
            final_text += first
            if first in self._rows:
                if second in self._cols:
                    if first + second in self._viable_coords:
                        final_text += second
            else:
                if second in self._rows:
                    if second + first in self._viable_coords:
                        final_text = second + final_text
        self.coords_input.ChangeValue(final_text)
        if final_text in self._viable_coords:
            self.OnChoice(final_text)
        else:
            self.coords_input.ChangeValue(self._default_coords)
            if self._shape_panel is not None:
                self._shape_panel.cut_cleanup()
            self.cutoffButton.Disable()
            self.cutoutButton.Disable()

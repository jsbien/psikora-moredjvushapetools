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


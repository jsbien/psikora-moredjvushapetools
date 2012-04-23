# -*- coding: utf-8 -*-
'''
Created on Apr 17, 2012

@author: zasvid
'''

import wx


class ChooseDocumentDialog(wx.Dialog):
    
    def __init__(self, data, parent, title):
        super(ChooseDocumentDialog, self).__init__(parent=parent, 
            title=title, size=(250, 200))

        self.data = data
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.ListBox(self, wx.ID_ANY)

        for i in range(len(self.data.documents)):
            self.listbox.Insert(self.data.documents[i].name, i, self.data.documents[i])
        
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Anuluj')
        button_sizer.Add(okButton)
        button_sizer.Add(closeButton, flag=wx.LEFT, border=5)

        okButton.Bind(wx.EVT_BUTTON, self.OnChoice)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
        sizer.Add(button_sizer, 1, flag= wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        self.SetSizer(sizer)
        
    def OnChoice(self, event):
        if self.listbox.GetSelection()!=-1:
            self.data.current_document = self.data.documents[self.listbox.GetSelection()]
        self.Close()
    
    def OnClose(self, event):
        self.Close()



class ChooseDictionaryDialog(wx.Dialog):
    
    def __init__(self, data, parent, title):
        super(ChooseDictionaryDialog, self).__init__(parent=parent, 
            title=title, size=(250, 200))

        self.data = data
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.ListBox(self, wx.ID_ANY)

        for i in range(len(self.data.shape_dictionaries)):
            self.listbox.Insert(self.data.shape_dictionaries[i].name, i, self.data.shape_dictionaries[i])
        
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Anuluj')
        button_sizer.Add(okButton)
        button_sizer.Add(closeButton, flag=wx.LEFT, border=5)

        okButton.Bind(wx.EVT_BUTTON, self.OnChoice)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
        sizer.Add(button_sizer, 1, flag= wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        self.SetSizer(sizer)
        
    def OnChoice(self, event):
        if self.listbox.GetSelection()!=-1:
            self.data.current_dictionary = self.data.shape_dictionaries[self.listbox.GetSelection()]
        self.Close()
    
    def OnClose(self, event):
        self.Close()


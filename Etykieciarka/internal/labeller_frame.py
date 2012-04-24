# -*- coding: utf-8 -*-
'''
@author: Piotr Sikora
'''

import wx
from database_manipulation import DatabaseManipulator
from internal.labeller_dialogs import *
from internal.labeller_data import LabellerData
from internal.labeller_hierarchy_panel import *
from internal.labeller_roots_panel import *
from internal.labeller_label_panel import *

class Labeller(wx.Frame):
    
    def __init__(self):
        self.data = LabellerData()
        
        wx.Frame.__init__(self, None, wx.ID_ANY, "Etykieciarka")
        
        # binding general behaviour
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        
        #building a menu
        menubar = wx.MenuBar()
        
        #first menu - database
        menu = wx.Menu()
        
        menuitem = menu.Append(wx.ID_EXIT, '&Wyjście', 'Wyjdź z programu')
        self.Bind(wx.EVT_MENU, self.OnQuit, menuitem)
        
        menuitem = menu.Append(wx.ID_ANY, 'Wybierz &Dokument', 'Wyświetla okno wyboru dokumentu z bazy')
        self.Bind(wx.EVT_MENU, self.OnChooseDocument, menuitem)

        menuitem = menu.Append(wx.ID_ANY, 'Wybierz &Słownik', 'Wyświetla okno wyboru słownika z bazy')
        self.Bind(wx.EVT_MENU, self.OnChooseDictionary, menuitem)

        
        menubar.Append(menu, '&Baza')
        
        #Help menu
        #menu = wx.Menu()
        
        #menuitem = menu.Append(wx.ID_ANY, '&O programie', "Informacje o programie")
        
        #menubar.Append(menu, '&Pomoc')
        
        self.SetMenuBar(menubar)
        
        self.SetSize((1024, 768))
        
        self.label_panel = LabelPanel(self, self.data)
        self.hierarchy_panel = HierarchyPanel(self, self.data, self.label_panel)
        self.roots_panel = RootsPanel(self, self.data, self.hierarchy_panel)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        innerSizer = wx.BoxSizer(wx.VERTICAL)
        
        innerSizer.Add(self.roots_panel,1, wx.EXPAND | wx.ALL, 5)
        innerSizer.Add(self.hierarchy_panel,5, wx.EXPAND | wx.ALL, 5)
        
        mainSizer.Add(innerSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.AddSpacer((5,5))
        mainSizer.Add(self.label_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(mainSizer)
        
        #global binding of keystrokes
        
        
        self.Centre()
        self.Show(True)
        
    def connect_to_database(self, db_name, db_host, db_user, db_pass):
        if hasattr(self,'db_manipulator'):
            del self.db_manipulator
        self.db_manipulator = DatabaseManipulator(db_name, db_host, db_user, db_pass)
        self.data.documents = self.db_manipulator.fetch_documents()

    def OnChooseDocument(self, event):
        self.choose_document()
        
    def choose_document(self):
        dialog = ChooseDocumentDialog(self.data, None, title='Wybierz dokument z bazy')
        dialog.ShowModal()
        dialog.Destroy()
        if self.data.current_document is not None:
            self.data.shape_dictionaries = self.db_manipulator.fetch_dictionaries(self.data.current_document.db_id)
        return (self.data.current_document is not None)
        #TODO: use Observers to observe when document changes (or at least check for change here)
        
    def OnChooseDictionary(self, event):
        self.choose_dictionary()
        
    def choose_dictionary(self):
        dialog = ChooseDictionaryDialog(self.data, None, title='Wybierz słownik kształtów z bazy')
        dialog.ShowModal()
        dialog.Destroy()
        if self.data.current_dictionary is not None:
            self.data.fill_shape_dicitonary(self.db_manipulator.fetch_shapes(self.data.current_dictionary.db_id))
        self.roots_panel.regenerate()
            
    def OnQuit(self, event):
        self.Close()
        self.DestroyChildren()
        self.Destroy()
            
    def OnExit(self, event):
        """ This method is called when exiting the application
            via menu or closing the application window.
        """
        if hasattr(self,'db_manipulator'):
            self.db_manipulator.close()
        # save the session
        self.save_session()
        event.Skip()
        
    def save_session(self):
        pass

    def load_session(self):
        pass
    
    def load_last_session(self):
        if self.choose_document():
            self.choose_dictionary()  
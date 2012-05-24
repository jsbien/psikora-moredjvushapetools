# -*- coding: utf-8 -*-
'''
@author: Piotr Sikora
'''

import wx
from internal.database_manipulation import DatabaseManipulator
from dialogs import *
from internal.data import ShapeData
from shapes_panel import ShapesPanel 
from roots_panel import RootsPanel
from label_panel import LabelPanel

class ShapeBrowser(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.data = ShapeData()
        
        # binding general behaviour
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        
        #building a menu
        menubar = wx.MenuBar()
        
        # menu - database
        menu = wx.Menu()
        
        menuitem = menu.Append(wx.ID_EXIT, '&Wyjście', 'Wyjdź z programu')
        self.Bind(wx.EVT_MENU, self.OnQuit, menuitem)
        
        menuitem = menu.Append(wx.ID_ANY, 'Wybierz &Dokument', 'Wyświetla okno wyboru dokumentu z bazy')
        self.Bind(wx.EVT_MENU, self.OnChooseDocument, menuitem)

        menuitem = menu.Append(wx.ID_ANY, 'Wybierz &Słownik', 'Wyświetla okno wyboru słownika z bazy')
        self.Bind(wx.EVT_MENU, self.OnChooseDictionary, menuitem)

        
        menubar.Append(menu, '&Baza')
        
        # menu - database
        menu = wx.Menu()
        
        menuitem = menu.Append(wx.ID_ANY, '&Wyłącz sortowanie', 'Wyłącza sortowanie korzeni hierarchii kształtów')
        self.Bind(wx.EVT_MENU, self.SortRootsNone, menuitem)
        
        menuitem = menu.Append(wx.ID_ANY, 'Sortowanie wg &rozmiaru', 'Sortuje korzenie hierarchii kształtów wg rozmiaru kształtu')
        self.Bind(wx.EVT_MENU, self.SortRootsSize, menuitem)
        
        menuitem = menu.Append(wx.ID_ANY, 'Sortowanie wg &liczebności', 'Sortuje korzenie hierarchii kształtów wg liczebności hierarchii')
        self.Bind(wx.EVT_MENU, self.SortRootsCount, menuitem)
        
        menubar.Append(menu, '&Hierarchie')
        
        #Help menu
        #menu = wx.Menu()
        
        #menuitem = menu.Append(wx.ID_ANY, '&O programie', "Informacje o programie")
        
        #menubar.Append(menu, '&Pomoc')
        
        self.SetMenuBar(menubar)
        
        self.SetSize((1024, 768))
        
        self.label_panel = LabelPanel(parent = self, data = self.data)
        self.shapes = ShapesPanel(data = self.data, target_panel = self.label_panel, parent = self)
        self.roots_panel = RootsPanel(parent = self, sorting_method = "count", data = self.data, target_panel = self.shapes)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        innerSizer = wx.BoxSizer(wx.VERTICAL)
        
        innerSizer.Add(self.roots_panel,1, wx.EXPAND | wx.ALL, 5)
        innerSizer.Add(self.shapes,5, wx.EXPAND | wx.ALL, 5)
        
        mainSizer.Add(innerSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.AddSpacer((5,5))
        mainSizer.Add(self.label_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(mainSizer)
        
        #TODO: global binding of keystrokes
        
        self.Centre()
        self.Show(True)
        
    def SortRootsNone(self, event):
        self.roots_panel.set_hierarchy_sorting_method(None)
        
    def SortRootsCount(self, event):
        self.roots_panel.set_hierarchy_sorting_method("count")
        
    def SortRootsSize(self, event):
        self.roots_panel.set_hierarchy_sorting_method("size")
    
    def connect_to_database(self, db_name, db_host, db_user, db_pass):
        if hasattr(self,'db_manipulator'):
            del self.db_manipulator
        self.db_manipulator = DatabaseManipulator(db_name, db_host, db_user, db_pass)
        self.data.documents = self.db_manipulator.fetch_documents()

    def OnChooseDocument(self, event):
        self.choose_document()
        
    def choose_document(self):
        previous_document = self.data.current_document
        dialog = ChooseDocumentDialog(data = self.data, title='Wybierz dokument z bazy', parent = None)
        dialog.ShowModal()
        dialog.Destroy()
        if self.data.current_document is not None:
            self.data.shape_dictionaries = self.db_manipulator.fetch_dictionaries(self.data.current_document.db_id)
        #reset data after document change
        if self.data.current_document != previous_document:
            self.data.current_dictionary = None
            self.data.shape_hierarchies = []
            self.data.current_hierarchy = None
            self.data.current_shape = None
            self.label_panel.regenerate()
            self.roots_panel.regenerate()
            self.shapes.regenerate()
        return (self.data.current_document is not None)
        #TODO: use Observers to observe when document changes (or at least check for change here)
        
    def OnChooseDictionary(self, event):
        self.choose_dictionary()
        
    def choose_dictionary(self):
        dialog = ChooseDictionaryDialog(data = self.data, parent = None, title='Wybierz słownik kształtów z bazy')
        dialog.ShowModal()
        dialog.Destroy()
        if self.data.current_dictionary is not None:
            self.data.fill_shape_dictionary(self.db_manipulator.fetch_shapes(self.data.current_dictionary.db_id))
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
        #TODO: temporary test
        self.data.current_document = self.data.documents[0]
        self.data.shape_dictionaries = self.db_manipulator.fetch_dictionaries(self.data.current_document.db_id)
        self.data.current_dictionary = self.data.shape_dictionaries[0]
        self.data.fill_shape_dictionary(self.db_manipulator.fetch_shapes(self.data.current_dictionary.db_id))
        self.data.current_hierarchy = self.data.shape_hierarchies[0]
        self.data.current_shape = self.data.shape_hierarchies[0]
        self.roots_panel.regenerate()
        self.shapes.regenerate()
        self.label_panel.regenerate()
        #if self.choose_document():
         #   self.choose_dictionary()  
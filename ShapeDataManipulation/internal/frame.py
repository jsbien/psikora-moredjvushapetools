# -*- coding: utf-8 -*-
'''
@author: Piotr Sikora
'''

import wx
from internal.database_manipulation import DatabaseManipulator
from internal.dialogs import *
from internal.data import ShapeData

class DjVuShapeToolsFrame(wx.Frame):
    
    def _add_menu_item(self, menu, text, help, binding, kind = wx.ITEM_NORMAL, id = wx.ID_ANY):
        item = menu.Append(id, text, help, kind)
        self.Bind(wx.EVT_MENU, binding, item)
        return item
    
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.data = ShapeData()

        # binding general behaviour
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        
        #building a menu
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.toolbar = self.CreateToolBar()
        self.new_document = False

        
    def connect_to_database(self, db_name, db_host, db_user, db_pass):
        if hasattr(self,'db_manipulator'):
            del self.db_manipulator
        self.db_manipulator = DatabaseManipulator(db_name, db_host, db_user, db_pass)
        self.data.db_manipulator = self.db_manipulator
        self.data.documents = self.db_manipulator.fetch_documents()
        
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
            self.new_document = True
        return (self.data.current_document is not None, )
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

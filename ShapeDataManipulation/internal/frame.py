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
from internal.database_manipulation import DatabaseManipulator
from internal.dialogs import *
from internal.data import ShapeData

class DjVuShapeToolsFrame(wx.Frame):
    
    def _add_menu_item_by_key(self, menu, menu_key, binding, kind = wx.ITEM_NORMAL, id = wx.ID_ANY):
        text, help = self._menuitem_strings[menu_key]
        item =  self._add_menu_item(menu, text, help, binding, kind, id)
        self._menu_items[menu_key] = item
        return item
    
    def _add_menu_item(self, menu, text, help, binding, kind = wx.ITEM_NORMAL, id = wx.ID_ANY):
        item = menu.Append(id, text, help, kind)
        self.Bind(wx.EVT_MENU, binding, item)
        return item
    
    def _append_menu(self, menubar, menu, menu_string):
        menubar.Append(menu, self._menu_strings[menu_string])
        self._menus[menu_string] = menu

    def _enable_menu_item(self, menu_key, menuitem_key, enable = True):
        menu = self._menus[menu_key] 
        menuitem_id = self._menu_items[menuitem_key].GetId()
        menu.Enable(menuitem_id, enable) 
    
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self._menu_strings = {}
        self._menuitem_strings = {}
        self.data = ShapeData()

        # binding general behaviour
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        
        #building a menu
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.toolbar = self.CreateToolBar()
        self.new_document = False
        self._menu_items = {}
        self._menus = {}
        
    def connect_to_database(self, db_name, db_host, db_user, db_pass):
        if hasattr(self,'db_manipulator'):
            del self.db_manipulator
        self.db_manipulator = DatabaseManipulator(db_name, db_host, db_user, db_pass)
        self.data.db_manipulator = self.db_manipulator
        self.data.documents = self.db_manipulator.fetch_documents()
        self.data.unicode_chars, self.data.uchars_by_id = self.db_manipulator.fetch_character_data()
        
    def choose_document(self):
        previous_document = self.data.current_document
        dialog = ChooseDocumentDialog(data = self.data, title='Wybierz dokument z bazy', parent = None)
        dialog.ShowModal()
        dialog.Destroy()
        if self.data.current_document is not None:
            self.data.shape_dictionaries = self.db_manipulator.fetch_dictionaries(self.data.current_document.db_id)
            self.data.pages = self.db_manipulator.fetch_pages(self.data.current_document.db_id)
        #reset data after document change
        if self.data.current_document != previous_document:
            self.data.current_dictionary = None
            self.data.shape_hierarchies = []
            self.data.current_hierarchy = None
            self.data.current_shape = None
            self.new_document = True
        return self.data.current_document is not None
        #TODO: use Observers to observe when document changes (or at least check for change here)

    def OnChooseDictionary(self, event):
        self.choose_dictionary()
        
    def choose_dictionary(self):
        dialog = ChooseDictionaryDialog(data = self.data, parent = None, title='Wybierz słownik kształtów z bazy')
        dialog.ShowModal()
        dialog.Destroy()
        if self.data.current_dictionary is not None:
            self.data.fill_shape_dictionary(
                        self.db_manipulator.fetch_shapes(self.data.current_dictionary.db_id)
                        )
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

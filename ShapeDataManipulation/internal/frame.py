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
import internal.strings as strings
import os, sys

__SCRIPT_PATH__ = os.path.abspath(os.path.dirname(sys.argv[0]))

def i18n(string):
    return string

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
        self.statusbar = self.CreateStatusBar()
        self.new_document = False
        
        self._menu_items = {}
        self._menus = {}
        
        self._menuitem_strings = strings.menuitems
        self._menu_strings = strings.menu
        self._app_data = strings.app_data
        self._app_data['AppName']=  self.GetTitle()
        self._temporary_status = ''
         
    def on_about(self, event):
        message = self._app_data.get('AppName', '') + ' ' + self._app_data.get('AppVersion','') + '\n'
        message += i18n('Author') + ': ' + self._app_data.get('Author','') + '\n'
        message += i18n('License') + ': ' + self._app_data.get('License','') + '\n'
        message += i18n('Website') + ': '  + self._app_data.get('Website','') + '\n'
        message += self._app_data.get('Notes','')
        wx.MessageBox(message = message, caption = i18n(u'About…'))

    def on_shortcuts(self, event):
        msg = u''
        for menustring, help_text in self._menuitem_strings.values():
            find_shortcut = menustring.split('\t')
            if len(find_shortcut) == 2:
                msg += unicode(find_shortcut[1]) + u" : • " + unicode(help_text) + u'\n'
        wx.MessageBox(message=msg, caption=u'Skróty klawiaturowe')
        
        
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
            self.statusbar.SetStatusText("Dane dokumentu: " + str(self.data.current_document.address) + " zostały wczytane z bazy. ")
        #reset data after document change
        if self.data.current_document != previous_document:
            self.data.current_dictionary = None
            self.data.shape_hierarchies = []
            self.data.current_hierarchy = None
            self.data.current_shape = None
            self.new_document = True
        return self.data.current_document is not None
        #TODO: use Observers to observe when document changes (or at least check for change here)

    def temporary_status(self, text):
        status = self.statusbar.GetStatusText()
        status = status[ : len(status) - len(self._temporary_status)]
        self._temporary_status = text
        self.statusbar.SetStatusText(status + text)

    def OnChooseDictionary(self, event):
        self.choose_dictionary()

    def OnEditHierarchy(self, event):
        if self.data.current_hierarchy is not None: 
            if self.data.current_hierarchy.children:
                dialog = ChooseCutShapeDialog(shapes_panel = self.shapes_panel,
                                       title=self._menuitem_strings['EditHierarchy'][0].split('\t')[0], parent = None)
                dialog.ShowModal()
                dialog.Destroy()
            else:
                dlg = wx.MessageDialog(self, "Hierarchia składająca się z 1 kształtu nie może być edytowana.", "Uwaga!", wx.OK | wx.ICON_WARNING)
                dlg.ShowModal()
                dlg.Destroy()
        
    def choose_dictionary(self):
        dialog = ChooseDictionaryDialog(data = self.data, parent = None, title='Wybierz słownik kształtów z bazy')
        dialog.ShowModal()
        dialog.Destroy()
        if self.data.current_dictionary is not None:
            self.data.fill_shape_dictionary(
                        self.db_manipulator.fetch_shapes(self.data.current_dictionary.db_id)
                        )
            self.data.load_labels(only_current_dictionary = True)
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

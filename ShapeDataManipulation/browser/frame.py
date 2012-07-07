# -*- coding: utf-8 -*-
'''
    Browser of DjVu shapes    
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

from internal.frame import DjVuShapeToolsFrame
from internal.shapes_panel import ShapesPanel 
from browser.roots_panel import RootsPanel
from internal.label_panel import LabelPanel

class ShapeBrowser(DjVuShapeToolsFrame):
    
    def __init__(self, *args, **kwargs):
        DjVuShapeToolsFrame.__init__(self, *args, **kwargs)
        menu = wx.Menu()
        self._add_menu_item(menu, 'Wybierz &Dokument', 'Wyświetla okno wyboru dokumentu z bazy' , binding = self.OnChooseDocument)
        self._add_menu_item(menu, 'Wybierz &Słownik', 'Wyświetla okno wyboru słownika z bazy', binding = self.OnChooseDictionary)
        self._add_menu_item(menu, '&Wyjście', 'Wyjdź z programu', binding = self.OnQuit)
        self.menubar.Append(menu, '&Baza')
        menu = wx.Menu()
        self._add_menu_item(menu, '&Wyłącz sortowanie', 'Wyłącza sortowanie korzeni hierarchii kształtów' , binding = self.SortRootsNone)
        self._add_menu_item(menu, 'Sortowanie wg &rozmiaru', 'Sortuje korzenie hierarchii kształtów wg rozmiaru kształtu' , binding = self.SortRootsSize)
        self._add_menu_item(menu, 'Sortowanie wg &liczebności', 'Sortuje korzenie hierarchii kształtów wg liczebności hierarchii' , binding = self.SortRootsCount)
        self.menubar.Append(menu, '&Hierarchie')
        self.SetSize((1024, 768))
        
        self.label_panel = LabelPanel(parent = self, data = self.data)
        self.shapes = ShapesPanel(data = self.data, target_panel = self.label_panel, parent = self)
        self.roots_panel = RootsPanel(parent = self, sorting_method = "count", data = self.data, target_panel = self.shapes)
        self.shapes.callbacks.append(self.roots_panel)
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
    
    def OnChooseDocument(self, event):
        self.choose_document()
        if self.new_document:
            self.label_panel.regenerate()
            self.shapes.regenerate()
            self.roots_panel.regenerate()
            self.new_document = False
    
    def save_session(self):
        pass

    def load_session(self):
        pass
    
    def load_last_session(self):
        #TODO: temporary test
        """
        self.data.current_document = self.data.documents[0]
        self.data.shape_dictionaries = self.db_manipulator.fetch_dictionaries(self.data.current_document.db_id)
        self.data.current_dictionary = self.data.shape_dictionaries[0]
        self.data.fill_shape_dictionary(self.db_manipulator.fetch_shapes(self.data.current_dictionary.db_id))
        self.data.current_hierarchy = self.data.shape_hierarchies[0]
        self.data.current_shape = self.data.shape_hierarchies[0]
        self.roots_panel.regenerate()
        self.shapes.regenerate()
        self.label_panel.regenerate()
        """
        if self.choose_document():
            self.choose_dictionary()  
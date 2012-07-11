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
from internal.image_conversion import PilImageToWxBitmap
from internal.datatypes import Label

from labeller.utils import unicode_code, unicode_name

_font_traits = ['font', 'font_type', 'font_size']
_combo_traits = _font_traits + ['textel_type']

_strings = {'title' : 'Dane kształtu',
            'db_id' : "Numer w słowniku kształtów:",
            'size'  : "Szerokość x Wysokość:",
            'textel' : "Tekstel:", 
            'textel_code' : "Kod tekstela: " ,
            'textel_name' : "Nazwa tekstela: " , 
            'textel_type' : "Typ tekstela:",
            'font_type' : "Postać fontu:",
            'font' : "Krój fontu:",
            'font_size' : "Rozmiar fontu:",
                        
            'no_label' : "Kształt niezaetykietowany.",
                         
            'doc_name' : "Dokument:",
            'doc_address' : "Adres dokumentu:",
            'dict_name' : "Nazwa słownika kształtów: ",
            'hierarchy_count' : "Liczba hierarchii w słowniku: ",
            'dict_shape_count' : "Liczba kształtów w słowniku: " 
            }

def _s(key):
    return _strings[key]


class LabelPanel(wx.Panel):
    
    def __init__(self, data, labelling = False, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.labelling = labelling
        self.data = data
        staticbox = wx.StaticBox(self, label = _s('title'))
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.VERTICAL)
        self.inner_panel = wx.Panel(self)
        sizer.Add(self.inner_panel, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        self._dirty = False
        self._last_values = None
        
    def layout_item(self, sizer, label_key, item):
        linesizer = wx.BoxSizer(wx.HORIZONTAL)
        infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, _s(label_key))
        linesizer.Add(infolabel, 0, wx.LEFT, 5)
        linesizer.AddStretchSpacer()
        linesizer.Add(item, 0, wx.RIGHT, 5)
        sizer.Add(linesizer, 0, wx.ALL | wx.EXPAND, 3)
        return item
        
    def label(self, value):
        return wx.StaticText(self.inner_panel, wx.ID_ANY, value)
    
    def combo(self, values, readonly = False):
        cb_style = wx.CB_DROPDOWN | wx.CB_SORT
        if readonly:
            cb_style = cb_style | wx.CB_READONLY
        return wx.ComboBox(self.inner_panel, choices = values, style = cb_style)

    def regenerate(self, unicode_chars = None):
        
        self._comboboxes = {}
        self.inner_panel.DestroyChildren()
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        if self.data.current_shape is not None:
            shape = self.data.current_shape
    
            imagepanel = wx.Panel(self.inner_panel)
            imagesizer = wx.BoxSizer(wx.VERTICAL)
            shapeImage = wx.StaticBitmap(imagepanel, -1, PilImageToWxBitmap(shape.image))
            imagesizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, 5)
            imagepanel.SetSizer(imagesizer)
            sizer.Add(imagepanel, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            
            self.layout_item(sizer, 'db_id', self.label(str(shape.id)))
            self.layout_item(sizer, 'size', self.label(str(shape.width) + " x " + str(shape.height)))
            sizer.Add(wx.StaticLine(parent = self.inner_panel), 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            if self.labelling:
                for char in unicode_chars:
                    self.layout_item(sizer, 'textel', self.label(char))
                    self.layout_item(sizer, 'textel_code', self.label(str(unicode_code(char))))
                    self.layout_item(sizer, 'textel_name', self.label(unicode_name(char)))
                self._comboboxes['textel_type'] = self.layout_item(sizer, 'textel_type', self.combo(self.data.textel_types, readonly = True))
                self._comboboxes['font_type'] = self.layout_item(sizer, 'font_type', self.combo(self.data.font_types.values()))
                self._comboboxes['font'] = self.layout_item(sizer, 'font', self.combo(self.data.fonts.values()))
                self._comboboxes['font_size'] = self.layout_item(sizer, 'font_size', self.combo(self.data.font_sizes.values()))
                if shape.label is None:
                    self._dirty = True
                    if self._last_values is None:
                        self._last_values = {}
                        if self.data.fonts:
                            self._last_values['font'] = self.data.fonts.values()[0]
                        if self.data.font_types:
                            self._last_values['font_type'] = self.data.font_types.values()[0]
                        if self.data.font_sizes:
                            self._last_values['font_size'] = self.data.font_sizes.values()[0]
                        self._last_values['textel_type'] = self.data.textel_types[0]
                    for combo_trait in _combo_traits:
                        if combo_trait in self._last_values:
                            self._comboboxes[combo_trait].SetStringSelection(self._last_values[combo_trait])
                    information = wx.StaticText(self.inner_panel, wx.ID_ANY, "Powyższe wartości są proponowane.")
                    information.SetForegroundColour('#FF0000')
                    sizer.Add(information, 0, wx.ALL | wx.EXPAND, 5)
                else: #default values
                    self._comboboxes['textel_type'].SetStringSelection(shape.label.textel_type)
                    self._comboboxes['font'].SetStringSelection(shape.label.font)
                    self._comboboxes['font_size'].SetStringSelection(shape.label.font_size)
                    self._comboboxes['font_type'].SetStringSelection(shape.label.font_type)
            else:
                if shape.label is None:
                    self.layout_item(sizer, 'no_label', self.label(""))
                else:
                    self.layout_item(sizer, 'textel', self.label(str(shape.label.textel)))
                    self.layout_item(sizer, 'textel_type', self.label(str(shape.label.textel_type)))
                    self.layout_item(sizer, 'font_type', self.label(str(shape.label.font_types)))
                    self.layout_item(sizer, 'font', self.label(str(shape.label.fonts)))
                    self.layout_item(sizer, 'font_size', self.label(str(shape.label.font_sizes)))
            sizer.AddStretchSpacer()
            #sizer.Add(wx.StaticLine(parent = self.inner_panel), 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            if not self.labelling:
                # self.layout_item(sizer, 'doc_name', self.label(str(self.data.current_document.name)))
                # self.layout_item(sizer, 'doc_address', self.label(str(self.data.current_document.address)))
                self.layout_item(sizer, 'dict_name', self.label(str(self.data.current_dictionary.name)))
                self.layout_item(sizer, 'hierarchy_count', self.label(str(len(self.data.shape_hierarchies))))
                self.layout_item(sizer, 'dict_shape_count', self.label(str(len(self.data.shapes))))
    
        self.inner_panel.SetSizer(sizer, True)
        self.inner_panel.Fit()
        self.inner_panel.Layout()
        self.inner_panel.Refresh()
        self.inner_panel.Update()

    def _save_font_trait(self, font_trait, data_dict):
        #font_trait_value =  u"%s" % self._comboboxes[font_trait].GetValue()
        font_trait_value =  self._comboboxes[font_trait].GetValue()
        db_id = None
        if font_trait_value not in data_dict.values():
            db_id = self.data.db_manipulator.insert_simple(font_trait + 's', font_trait, font_trait_value)
            data_dict[db_id] = font_trait_value
        else:
            for key in data_dict:
                if data_dict[key] == font_trait_value:
                    db_id = key
                    break
        self._last_values[font_trait] = font_trait_value
        return (db_id, font_trait_value)
        

    def save_label(self, unicode_character):
        if self._dirty:
            self._dirty = False
            font_id, font = self._save_font_trait('font', self.data.fonts)
            font_type_id, font_type = self._save_font_trait('font_type', self.data.font_types)
            font_size_id, font_size = self._save_font_trait('font_size', self.data.font_sizes)
            #save unicode character
            uchar_id = self.data.uchar_id(unicode_character, unicode_name(unicode_character))
            textel_type = self._comboboxes['textel_type'].GetValue()
            self._last_values['textel_type'] = textel_type
            #save a label
            label = Label(font_id = font_id, font = font,
                      font_type_id = font_type_id, font_type = font_type,
                      font_size_id = font_size_id, font_size = font_size,
                      textel_id = uchar_id, textel = unicode_character, 
                      textel_type = textel_type
                      )
            self.data.current_shape.label = label
            label.db_id = self.data.db_manipulator.insert_label(label, self.data.user_id(self.data.db_manipulator.db_user), self.data.current_document.db_id)
        
            #save a link between label and uchar
            self.data.db_manipulator.insert_into_junction(table = "label_chars", fields = ("uchar_id","label_id"), values = (uchar_id, label.db_id))
        
            #label the hierarchy of shapes
            for shape in self.data.current_hierarchy.linearise_hierarchy():
                self.data.db_manipulator.insert_into_junction(table = "labelled_shapes", fields = ("shape_id", "label_id"), values = (shape.db_id, label.db_id))

                    
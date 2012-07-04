# -*- coding: utf-8 -*-
'''
Created on Apr 18, 2012

@author: Piotr Sikora
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
        
    def label_layout(self, sizer, label, value):
        linesizer = wx.BoxSizer(wx.HORIZONTAL)
        infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, label)
        valuelabel = wx.StaticText(self.inner_panel, wx.ID_ANY, value)
        linesizer.Add(infolabel, 0, wx.ALL, 5)
        linesizer.AddStretchSpacer()
        linesizer.Add(valuelabel, 0, wx.ALL, 5)
        sizer.Add(linesizer, 0, wx.ALL | wx.EXPAND, 5)
    
    def combo_layout(self, sizer, label_key, values, readonly = False):
        linesizer = wx.BoxSizer(wx.HORIZONTAL)
        infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, _s(label_key))
        cb_style = wx.CB_DROPDOWN | wx.CB_SORT
        if readonly:
            cb_style = cb_style | wx.CB_READONLY
        valuebox = wx.ComboBox(self.inner_panel, choices = values, style = cb_style)
        linesizer.Add(infolabel, 0, wx.ALL, 5)
        linesizer.AddStretchSpacer()
        linesizer.Add(valuebox, 0, wx.ALL, 5)
        sizer.Add(linesizer, 0, wx.ALL | wx.EXPAND, 5)
        self._comboboxes[label_key] = valuebox

    def text_control_layout(self, sizer, label, initial_value):
        linesizer = wx.BoxSizer(wx.HORIZONTAL)
        infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, label)
        valuechanger = wx.TextCtrl(self.inner_panel)
        #valuelabel = wx.StaticText(self.inner_panel, wx.ID_ANY, value)
        linesizer.Add(infolabel, 0, wx.ALL, 5)
        linesizer.AddStretchSpacer()
        linesizer.Add(valuechanger, 0, wx.ALL, 5)
        sizer.Add(linesizer, 0, wx.ALL | wx.EXPAND, 5)
        
    def regenerate(self, unicode_char = None):
        
        self._comboboxes = {}
        self.inner_panel.DestroyChildren()
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        if self.data.current_shape is not None:
            shape = self.data.current_shape
    
            imagepanel = wx.Panel(self.inner_panel)
            imagesizer = wx.BoxSizer(wx.VERTICAL)
            shapeImage = wx.StaticBitmap(imagepanel, -1, PilImageToWxBitmap(shape.get_image()))
            imagesizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, 5)
            imagepanel.SetSizer(imagesizer)
            sizer.Add(imagepanel, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            
            self.label_layout(sizer, _s('db_id'), str(shape.id))
            self.label_layout(sizer, _s('size'), str(shape.width) + " x " + str(shape.height))
            sizer.Add(wx.StaticLine(parent = self.inner_panel), 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            if self.labelling:
                self.label_layout(sizer, _s('textel'), unicode_char)
                self.label_layout(sizer, _s('textel_code'), str(unicode_code(unicode_char)))
                self.label_layout(sizer, _s('textel_name'), unicode_name(unicode_char))
                self.combo_layout(sizer, 'textel_type', self.data.textel_types, readonly = True)
                self.combo_layout(sizer, 'font_type', self.data.font_types.values())
                self.combo_layout(sizer, 'font', self.data.fonts.values())
                self.combo_layout(sizer, 'font_size', self.data.font_sizes.values())
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
                    self.label_layout(sizer, _s('no_label'), "")
                else:
                    self.label_layout(sizer, _s('textel'), str(shape.label.textel))
                    self.label_layout(sizer, _s('textel_type'), str(shape.label.textel_type))
                    self.label_layout(sizer, _s('font_type'), str(shape.label.font_types))
                    self.label_layout(sizer, _s('font'), str(shape.label.fonts))
                    self.label_layout(sizer, _s('font_size'), str(shape.label.font_sizes))
            sizer.AddStretchSpacer()
            sizer.Add(wx.StaticLine(parent = self.inner_panel), 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            self.label_layout(sizer, _s('doc_name'), str(self.data.current_document.name))
            self.label_layout(sizer, _s('doc_address'), str(self.data.current_document.address))
            if not self.labelling:
                self.label_layout(sizer, _s('dict_name'), str(self.data.current_dictionary.name))
                self.label_layout(sizer, _s('hierarchy_count'), str(len(self.data.shape_hierarchies)))
                self.label_layout(sizer, _s('dict_shape_count'), str(len(self.data.shapes)))
    
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

                    
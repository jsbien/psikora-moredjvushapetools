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
import traceback 

import wx
import wx.lib.scrolledpanel
from internal.image_conversion import PilImageToWxBitmap
from internal.datatypes import Label

from labeller.utils import unicode_codestr, unicode_names
from wx._core import EVT_CHECKBOX

_font_traits = ['font', 'font_type', 'font_size']
_combo_traits = _font_traits + ['textel_type']

_colors = {'red' : '#FF0000',
           'green' : '#00FF00'
          }

_strings = {'shape_title' : 'Dane kształtu',
            'label_title' : 'Etykieta hierarchii kształtów',
            'db_id' : "Numer w słowniku kształtów:",
            'size'  : "Szerokość x Wysokość:",
            'noise' : 'Szum',
            'textel' : "Tekstel:", 
            'textel_code' : "Kod tekstela: " ,
            'textel_name' : "Nazwa tekstela: " , 
            'textel_type' : "Typ tekstela:",
            'font_type' : "Postać fontu:",
            'font' : "Krój fontu:",
            'font_size' : "Rozmiar fontu:",
                        
            'no_label' : "Kształt niezaetykietowany.",
            'approve label' : u"Zatwierdź etykietę",   
            'doc_name' : "Dokument:",
            'doc_address' : "Adres dokumentu:",
            'dict_name' : "Nazwa słownika kształtów: ",
            'hierarchy_count' : "Liczba hierarchii w słowniku: ",
            'dict_shape_count' : "Liczba kształtów w słowniku: " 
            }

def _s(key):
    return _strings[key]

class LabelPanel(wx.Panel):
    
    def __init__(self, data, labelling = False, hierarchy_mode = False, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.labelling = labelling
        self.data = data
        if hierarchy_mode or labelling:
            title_key = 'label_title'
        else: 
            title_key = 'shape_title'
        staticbox = wx.StaticBox(self, label = _s(title_key))
        sizer = wx.StaticBoxSizer(staticbox, orient = wx.VERTICAL)
        self.inner_panel = wx.Panel(self)
        sizer.Add(self.inner_panel, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        self._dirty = False
        self._last_values = {}  
        self._items = {}
        self.hierarchy_mode = hierarchy_mode
        self._messages = {}
        
    def layout_item(self, sizer, label_key, item):
        self._items[label_key] = item
        linesizer = wx.BoxSizer(wx.HORIZONTAL)
        infolabel = wx.StaticText(self.inner_panel, wx.ID_ANY, _s(label_key))
        self._infolabels[label_key] = infolabel
        linesizer.Add(infolabel, 0, wx.LEFT | wx.CENTER, 5)
        linesizer.AddStretchSpacer()
        linesizer.Add(item, 0, wx.RIGHT | wx.CENTER, 5)
        sizer.Add(linesizer, 0, wx.ALL | wx.EXPAND, 3)
        return item
        
    def label(self, value):
        return wx.StaticText(self.inner_panel, wx.ID_ANY, value)
    
    def combobox(self, values, readonly = False):
        cb_style = wx.CB_DROPDOWN | wx.CB_SORT
        if readonly:
            cb_style = cb_style | wx.CB_READONLY
        return wx.ComboBox(self.inner_panel, choices = values, style = cb_style)

    def textctrl(self, value):
        textctrl = wx.TextCtrl(self.inner_panel)
        textctrl.ChangeValue(value)
        return textctrl

    def init_last_values(self):
        if self.data.fonts:
            self._last_values['font'] = self.data.fonts.values()[0]
        if self.data.font_types:
            self._last_values['font_type'] = self.data.font_types.values()[0]
        if self.data.font_sizes:
            self._last_values['font_size'] = self.data.font_sizes.values()[0]
        self._last_values['textel_type'] = self.data.textel_types[0]

    def _is_dirty(self):
        return self._dirty
    def _set_dirty(self, value):
        self._dirty = value
        self._change_feedback_labels()
    dirty = property(_is_dirty, _set_dirty)

    def _textel_is_important(self):
        if len(self._items['textel'].GetValue()) == 0:
            for combobox in self._comboboxes.values():
                combobox.Hide()
            self._items['approve label'].Enable(False)
        else:
            self._items['approve label'].Enable(True)
            for combobox in self._comboboxes.values():
                combobox.Show()

    def _print_messages(self, sizer):
        self._messages['no label'] = self._message_label(sizer, "Hierarchia kształtów nie jest zaetykietowana.\nPowyższe wartości są proponowane.", 'red')

    def _message_label(self, sizer, content, color):
        message = wx.StaticText(self.inner_panel, wx.ID_ANY, content)
        message.SetForegroundColour(_colors[color])
        sizer.Add(message, 0, wx.ALL | wx.EXPAND, 5)
        return message

    def show_message(self, key, show = True):
        if key in self._messages:
            self._messages[key].Show(show)
        
    def hide_message(self, key):
        self.show_message(key, False)

    def _change_feedback_labels(self):
        if not self.labelling:
            return
        if 'textel' in self._items:
            textel_len = len(self._items['textel'].GetValue()) if self._textel_ctrl else len(self._items['textel'].GetLabel())
        else:
            textel_len = 0
        if textel_len == 0 and not self._items['noise'].GetValue():
            self._infolabels['approve label'].SetForegroundColour('#FF0000')
            self._infolabels['approve label'].SetLabel('Wpisz tekstel lub oznacz kształty jako szum.')
            self._items['approve label'].Enable(False)
        elif self.dirty:
            self._infolabels['approve label'].SetForegroundColour('#0000FF')
            self._infolabels['approve label'].SetLabel('Nowa etykieta nie jest zapisana.')
            self._items['approve label'].Enable()
        else:
            self._infolabels['approve label'].SetLabel('')
            self._items['approve label'].Enable(False)
        if self.data.current_hierarchy is not None and self.data.current_hierarchy.label is not None:
            if self.dirty:
                self._infolabels['approve label'].SetForegroundColour('#0000FF')
                self._infolabels['approve label'].SetLabel('Etykieta zmodyfikowana.')
                self._items['approve label'].Enable(True)
            else:
                self._infolabels['approve label'].SetForegroundColour('#00FF00')
                self._infolabels['approve label'].SetLabel('Hierarchia jest zaetykietowana.')
                self._items['approve label'].Enable(False)
            self.hide_message('no label')

            
    def regenerate(self, unicode_chars = None, keep_last_values = False):
        self._dirty = False
        self._comboboxes = {}
        if keep_last_values:
            pass
        self.inner_panel.DestroyChildren()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._items = {}
        self._infolabels = {}
        if self.data.current_hierarchy is not None:
            shape = self.data.current_shape
            if not self.hierarchy_mode:
                imagepanel = wx.Panel(self.inner_panel)
                imagesizer = wx.BoxSizer(wx.VERTICAL)
                shapeImage = wx.StaticBitmap(imagepanel, -1, PilImageToWxBitmap(shape.image))
                imagesizer.Add(shapeImage, 1, wx.ALIGN_CENTER | wx.ALL, 5)
                imagepanel.SetSizer(imagesizer)
                sizer.Add(imagepanel, 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
                self.layout_item(sizer, 'db_id', self.label(str(shape.id)))
                self.layout_item(sizer, 'size', self.label(str(shape.width) + " x " + str(shape.height)))
                sizer.Add(wx.StaticLine(parent = self.inner_panel), 0, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 5)
            if not self.labelling:
                self.layout_item(sizer, 'dict_name', self.label(str(self.data.current_dictionary.name)))
                self.layout_item(sizer, 'hierarchy_count', self.label(str(len(self.data.shape_hierarchies))))
                self.layout_item(sizer, 'dict_shape_count', self.label(str(len(self.data.shapes))))
            if self.labelling:
                shape = self.data.current_hierarchy
                noise_check = self.layout_item(sizer, 'noise', wx.CheckBox(self.inner_panel))
                noise_check.Bind(wx.EVT_CHECKBOX, self.OnNoiseToggle)
                if unicode_chars is None:
                    if shape.label is not None:
                        textel = str(shape.label)
                    else:
                        textel = ''
                    textelCtrl = self.layout_item(sizer, 'textel', self.textctrl(textel))
                    textelCtrl.Bind(wx.EVT_TEXT, self.OnTextelChange)
                    self.layout_item(sizer, 'textel_code', self.label(unicode_codestr(textel)))
                    self.layout_item(sizer, 'textel_name', self.label(unicode_names(textel)))
                    self._textel_ctrl = True
                else:
                    self.layout_item(sizer, 'textel', self.label(unicode_chars))
                    self.layout_item(sizer, 'textel_code', self.label(unicode_codestr(unicode_chars)))
                    self.layout_item(sizer, 'textel_name', self.label(unicode_names(unicode_chars)))
                    self._textel_ctrl = False
                self._comboboxes['textel_type'] = self.layout_item(sizer, 'textel_type', self.combobox(self.data.textel_types, readonly = True))
                self._comboboxes['font_type'] = self.layout_item(sizer, 'font_type', self.combobox(self.data.font_types.values()))
                self._comboboxes['font'] = self.layout_item(sizer, 'font', self.combobox(self.data.fonts.values()))
                self._comboboxes['font_size'] = self.layout_item(sizer, 'font_size', self.combobox(self.data.font_sizes.values()))
                for combobox in self._comboboxes.values():
                    combobox.Bind(wx.EVT_TEXT, self.OnComboEdit)
                    combobox.Bind(wx.EVT_COMBOBOX, self.OnComboEdit)
                button = self.layout_item(sizer, 'approve label', wx.Button(self.inner_panel, label = _s('approve label')))
                if self.hierarchy_mode:
                    button.Bind(wx.EVT_BUTTON, self.OnSaveChanges)
                else:
                    button.Hide()
                self._print_messages(sizer)
                if shape.label is None or shape.label.noise:
                    self.dirty = True
                    if not self._last_values:
                        self.init_last_values()
                    for combo_trait in _combo_traits:
                        if combo_trait in self._last_values:
                            self._comboboxes[combo_trait].SetStringSelection(self._last_values[combo_trait])
                    self.show_message('no label')
                else:
                    self._comboboxes['textel_type'].SetStringSelection(shape.label.textel_type)
                    self._comboboxes['font'].SetStringSelection(shape.label.font)
                    self._comboboxes['font_size'].SetStringSelection(shape.label.font_size)
                    self._comboboxes['font_type'].SetStringSelection(shape.label.font_type)
                if shape.label is not None and shape.label.noise:
                    noise_check.SetValue(True)
                    self.dirty = False
                if self.hierarchy_mode:
                    self._textel_is_important()
            else:
                """
                if shape.label is None:
                    self.layout_item(sizer, 'no_label', self.label(""))
                else:
                    self.layout_item(sizer, 'textel', self.label(str(shape.label.textel)))
                    self.layout_item(sizer, 'textel_type', self.label(str(shape.label.textel_type)))
                    self.layout_item(sizer, 'font_type', self.label(str(shape.label.font_types)))
                    self.layout_item(sizer, 'font', self.label(str(shape.label.fonts)))
                    self.layout_item(sizer, 'font_size', self.label(str(shape.label.font_sizes)))
                """
                pass
            self._change_feedback_labels()
        sizer.AddStretchSpacer()
        self.inner_panel.SetSizer(sizer, True)
        self.inner_panel.Fit()
        self.inner_panel.Layout()
        self.inner_panel.Refresh()
        self.inner_panel.Update()

    def OnNoiseToggle(self, event):
        checkbox = self._items['noise']
        show = not checkbox.GetValue()
        self.dirty = True
        for key in self._items.keys():
            if key not in ['noise','db_id','size', 'approve label']:
                self._infolabels[key].Show(show)
                self._items[key].Show(show)
        if show and self.hierarchy_mode:
            self._textel_is_important()

    def OnTextelChange(self, event):
        textel = event.GetString()
        self.dirty = True
        self._items['textel_code'].SetLabel(unicode_codestr(textel))
        self._items['textel_name'].SetLabel(unicode_names(textel))
        self._textel_is_important()
        self._change_feedback_labels()
        self.inner_panel.Fit()

    def OnComboEdit(self, event):
        eventbox = event.GetEventObject()
        for key in self._comboboxes.keys():
            if self._comboboxes[key] == eventbox:
                if key not in self._last_values or eventbox.GetValue() != self._last_values[key]:
                    self.dirty = True

    def _remember_last_values(self):
        for font_trait in _combo_traits:
            self._last_values[font_trait] = self._comboboxes[font_trait].GetValue()
        
    def _save_font_trait(self, font_trait, data_dict):
        #font_trait_value =  u"%s" % self._comboboxes[font_trait].GetValue()
        font_trait_value = self._comboboxes[font_trait].GetValue()
        if font_trait_value == '':
            return (None, None)
        db_id = None
        self._last_values[font_trait] = font_trait_value
        if font_trait_value not in data_dict.values():
            db_id = self.data.db_manipulator.insert_simple(font_trait + 's', font_trait, font_trait_value)
            data_dict[db_id] = font_trait_value
        else:
            for key in data_dict:
                if data_dict[key] == font_trait_value:
                    db_id = key
                    break
        return (font_trait_value, db_id)

    def OnSaveChanges(self, event):
        self.save_changes()
       
    def save_changes(self):
        if 'textel' in self._items:
            characters = self._items['textel'].GetValue()
            if len(characters) == 0 and not self._items['noise'].GetValue():
                dial = wx.MessageDialog(None, 'Nie można zatwierdzić etykiety bez wypełnienia pola "tekstel" lub oznaczenia jej jako szum!', 'Uwaga', 
                                        wx.OK | wx.ICON_EXCLAMATION)
                dial.ShowModal()
            else:
                self.save_label(characters)
        self._change_feedback_labels()

    def save_label(self, unicode_characters):
        if self.dirty:
            noise = self._items['noise'].GetValue()
            traits = {}
            trait_ids = {}
            uchar_ids = []
            if noise:
                for trait in _combo_traits:
                    traits[trait] = None
                    trait_ids[trait] = None
            else:
                for trait, data_source in [('font', self.data.fonts), ('font_type', self.data.font_types), ('font_size', self.data.font_sizes)]: 
                    traits[trait], trait_ids[trait] = self._save_font_trait(trait, data_source) 
                #save unicode characters
                for unicode_character in unicode_characters:
                    uchar_ids.append(self.data.uchar_id(unicode_character, unicode_names(unicode_character)))
                traits['textel_type'] = self._comboboxes['textel_type'].GetValue()
                self._last_values['textel_type'] = traits['textel_type']
            #save a label
            label = Label(font_id = trait_ids['font'], font = traits['font'],
                      font_type_id = trait_ids['font_type'], font_type = traits['font_type'],
                      font_size_id = trait_ids['font_size'], font_size = traits['font_size'],
                      textel_ids = uchar_ids, textel = unicode_characters, 
                      textel_type = traits['textel_type'], noise = noise 
                      )
            if label.noise is None:
                raise ValueError
            if self.data.current_hierarchy.label is not None:
                label.db_id = self.data.current_hierarchy.label.db_id 
                self.data.db_manipulator.update_label(label, self.data.user_id(self.data.db_manipulator.db_user), self.data.current_document.db_id)
                #remove previous links between label and uchars
                label_id = self.data.current_hierarchy.label.db_id
                for uchar_id in self.data.current_hierarchy.label.textel_ids:
                    self.data.db_manipulator.remove_from_junction(table = "label_chars", fields = ("uchar_id", "label_id"), values = (uchar_id, label_id))
            else:
                label.db_id = self.data.db_manipulator.insert_label(label, self.data.user_id(self.data.db_manipulator.db_user), self.data.current_document.db_id)
                #add entries linking shapes in the hierarchy with a new label
                for shape in self.data.current_hierarchy.linearise_hierarchy():
                    self.data.db_manipulator.insert_into_junction(table = "labelled_shapes", fields = ("shape_id", "label_id"), values = (shape.db_id, label.db_id))
            #label the hierarchy of shapes
            for shape in self.data.current_hierarchy.linearise_hierarchy():
                shape.label = label

            #save a link between label and uchars
            for sequence in range(len(uchar_ids)):
                self.data.db_manipulator.insert_into_junction(table = "label_chars", fields = ("sequence", "uchar_id","label_id"), values = (sequence, uchar_ids[sequence], label.db_id))
                
                
            self.data.db_manipulator.commit()
            self.dirty = False

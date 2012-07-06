# -*- coding: utf-8 -*-
'''
@author: Piotr Sikora
'''

import wx
import wx.lib.ogl
import wx.lib.newevent
import wx.lib.scrolledpanel


from hocr_data import DatahOCR
from labeller.context import ContextPanel
from labeller.labelling import LabellingPanel
from internal.shapes_panel import ShapesPanel
import shelve
import os.path

import djvusmooth.models.text
from djvusmooth.gui.page import PageWidget, PercentZoom, OneToOneZoom, StretchZoom, FitWidthZoom, FitPageZoom

from djvusmooth.i18n import _
import djvu.decode
import djvu.const

from internal.frame import DjVuShapeToolsFrame
from labeller.utils import page_of_hocr_data
import sys


class hOCRLabeller(DjVuShapeToolsFrame):
    
    def __init__(self, *args, **kwargs):
        DjVuShapeToolsFrame.__init__(self, *args, **kwargs)

        wx.lib.ogl.OGLInitialize()

        self.data_hocr = DatahOCR(self.data)
        self.last_visited_directory = None
        self.context = Context(self)
        
        self._menuitem_strings = { 'ChooseDocument': ['Wybierz &Dokument', 'Wyświetla okno wyboru dokumentu z bazy'],
                'LoadHOCR': ['Otwórz pliki z &hOCR', 'Wyświetla okno wybór plików zawierających dane hOCR'],
                'Quit': ['&Wyjście', 'Wyjdź z programu'],
                'NextLine': ['Następny wiersz' + '\tCtrl+Alt+N', 'Przejdź do następnego wiersza'],
                'PrevLine': ['Poprzedni wiersz' + '\tCtrl+Alt+P', 'Przejdź do poprzedniego wiersza'],
                'NextChar': ['Następny kształt' + '\tCtrl+Shift+N', 'Przejdź do następnego kształtu bez zatwierdzenia etykiety'],
                'PrevChar': ['Poprzedni kształt' + '\tCtrl+P', 'Przejdź do poprzedniego kształtu bez zatwierdzenia etykiety'],
                'PrevCharToLabel': ['Poprzedni niezaetykietowany kształt' + '\tCtrl+W', 'Przejdź do poprzedniego niezaetykietowanego kształtu bez zatwierdzenia etykiety'],
                'NextCharCommit': ['Zatwierdź etykietę' + '\tCtrl+N', 'Przejdź do następnego kształtu, zatwierdzając etykietę dla obecnego'],
                'NextCharToLabel': ['Następny niezaetykietowany kształt' + '\tCtrl+Shift+E',
                                    'Przejdź do następnego niezaetykietowanego kształtu bez zatwierdzania etykiety'],
                'NextCharToLabelCommit': ['Zatwierdź etykietę 2' + '\tCtrl+E', 'Przejdź do następnego kształtu, zatwierdzając etykietę dla obecnego']
                }
        self._menu_strings = { 'Data' : '&Dane',
                              #'View' : _('&View'),
                              'View' : 'Widok',
                              'hOCR' : '&hOCR',
                              '' : ''
                            }
        
        # menu - database
        menu = wx.Menu()
        self._add_menu_item_by_key(menu, 'ChooseDocument', self.OnChooseDocument)
        self._add_menu_item_by_key(menu, 'LoadHOCR', binding = self.OnLoadHOCR)
        
        
        self._add_menu_item_by_key(menu, 'Quit', binding = self.OnQuit)
        self._append_menu(self.menubar, menu, 'Data')
        self._enable_menu_item('Data', 'LoadHOCR', False)
    
        menu = wx.Menu()
        self._add_menu_item_by_key(menu, 'NextLine', binding = self.OnNextLine)
        self._add_menu_item_by_key(menu, 'PrevLine', binding = self.OnPrevLine)
        self._add_menu_item_by_key(menu, 'NextChar', binding = self.OnNextChar)
        self._add_menu_item_by_key(menu, 'NextCharCommit', binding = self.OnNextCharCommit)
        self._add_menu_item_by_key(menu, 'NextCharToLabel', binding = self.OnNextCharToLabel)
        self._add_menu_item_by_key(menu, 'NextCharToLabelCommit', binding = self.OnNextCharToLabelCommit)
        self._add_menu_item_by_key(menu, 'PrevChar', binding = self.OnPrevChar)
      #  self._add_menu_item_by_key(menu, 'PrevCharCommit', binding = self.OnNextCharCommit)
        self._add_menu_item_by_key(menu, 'PrevCharToLabel', binding = self.OnPrevCharToLabel)
        #self._add_menu_item_by_key(menu, 'NextCharToLabelCommit', binding = self.OnNextCharToLabelCommit)
        
        self._append_menu(self.menubar, menu, 'hOCR')
        
        self._append_menu(self.menubar, self._create_view_menu(), 'View')

        #tool = toolbar.AddLabelTool(wx.ID_ANY, 'Prz', wx.Bitmap('texit.png'))
        #TODO: make icons
        self.toolbar.Realize()

        self.SetSize((1024, 768))
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        panel = self.context_panel = ContextPanel(parent = self, data = self.data, data_hocr = self.data_hocr)
        self.page_widget = self.context_panel.page_widget
        self.page_widget.render_mode = djvu.decode.RENDER_FOREGROUND
        mainSizer.Add(panel, 4, wx.EXPAND | wx.ALL, 1)
        
        panel = self.labelling_panel = LabellingPanel(parent = self, data = self.data, data_hocr = self.data_hocr)
        mainSizer.Add(panel, 5, wx.EXPAND | wx.ALL, 1)        

        self.SetSizer(mainSizer)

        #TODO: global binding of keystrokes
        self.page_widget.Bind(wx.EVT_CHAR, self.on_char)

        self.Maximize()
        self.Centre()
        self.Show(True)
    
    def OnChooseDocument(self, event):
        self.choose_document_for_labelling()
            
    def choose_document_for_labelling(self):
        if self.choose_document():
            self._enable_menu_item('Data', 'LoadHOCR')
            self.data_hocr.clear()
            return True
        return False
    
    def OnLoadHOCR(self, event):
        self.load_hocr_data()
    
    def OnNextLine(self, event):
        self.data_hocr.text_model.next_line()
        self.labelling_panel.regenerate()

    def OnPrevLine(self, event):
        self.data_hocr.text_model.prev_line()
        self.labelling_panel.regenerate()
 
    def OnPrevChar(self, event):
        self.data_hocr.next_shape(previous = True)
        self.labelling_panel.regenerate()
        
    def OnPrevCharCommit(self, event):
        self.labelling_panel.save_label()
        self.OnPrevChar(event)
        
    def OnPrevCharToLabel(self, event):
        self.data_hocr.next_shape(previous = True, find_unlabeled = True)
        self.labelling_panel.regenerate()
        
    def OnPrevCharToLabelCommit(self, event):
        self.labelling_panel.save_label()
        self.OnPrevCharToLabel(event)
        
    def OnNextChar(self, event):
        self.data_hocr.next_shape()
        self.labelling_panel.regenerate()
        
    def OnNextCharCommit(self, event):
        self.labelling_panel.save_label()
        self.OnNextChar(event)
        
    def OnNextCharToLabel(self, event):
        self.data_hocr.next_shape(find_unlabeled = True)
        self.labelling_panel.regenerate()
        
    def OnNextCharToLabelCommit(self, event):
        self.labelling_panel.save_label()
        self.OnNextCharToLabel(event)
        
    def load_hocr_data(self):
        path = self.open_directory("Wybierz katalog z dokumentem i danymi hOCR")
        doc_name = self.data.current_document.name
        if path is not None:
            listing = os.listdir(path)
            for filename in listing:
                page_data = page_of_hocr_data(path, filename, doc_name)
                if page_data is not None:
                    print("Opened " + str(path + os.sep + filename))
                    page_no, hocr_page = page_data
                    self.data_hocr.add_page(page_no, hocr_page)
            print(str("Trying to open: " + str(path + os.sep + doc_name)))
            self.open_djvu_file(path + os.sep + doc_name)
            
            
    def open_djvu_file(self, filename):
        try:
            self.data_hocr.document = self.context.new_document(djvu.decode.FileURI(filename))
            self.data_hocr.make_text_model([self])
            #self.update_title()
            self.context_panel.update_page_widget(new_document = True, new_page = True)
            self.labelling_panel.regenerate()
        except djvu.decode.JobFailed as exc:
            print("Opening djvu file failed: "+ str(sys.exc_info())
            self.data_hocr.text_model = None
            self.data_hocr.document = None
        
    def open_directory(self, dialog_title):
        if self.last_visited_directory is None:
            default_dir = "" #current_directory
        else:
            default_dir = self.last_visited_directory
        """
        Show the DirDialog and print the user's choice to stdout
        """
        dlg = wx.DirDialog(parent = self, message = dialog_title,
                           defaultPath = default_dir,
                           style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                       )
        chosen_path = None
        if dlg.ShowModal() == wx.ID_OK:
            chosen_path = dlg.GetPath()
            self.last_visited_directory = chosen_path
        dlg.Destroy()
        return chosen_path
        
    def save_session(self):
        session_file = shelve.open('last.session','n')
        session_file['last_visited_directory'] = self.last_visited_directory
        session_file.close()

    def load_session(self):
        session_file = shelve.open('last.session','r')
        self.last_visited_directory = session_file['last_visited_directory'] 
        session_file.close()
        
    def load_last_session(self):
        if os.path.isfile('last.session'):
            self.load_session() 
        if self.choose_document():
            self.load_hocr_data()

    def notify_page_change(self):
        self.context_panel.update_page_widget(new_page= True)

# Code taken from DJVUSMOOTH 
# 
# Copyright © 2008, 2009, 2010, 2011 Jakub Wilk <jwilk@jwilk.net>
# Copyright © 2009 Mateusz Turcza <mturcza@mimuw.edu.pl>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

    def _create_view_menu(self):
        menu = wx.Menu()
        submenu = wx.Menu()
        for caption, help, method, id in \
        [
            (_('Zoom &in'),  _('Increase the magnification'), self.on_zoom_in, wx.ID_ZOOM_IN),
            (_('Zoom &out'), _('Decrease the magnification'), self.on_zoom_out, wx.ID_ZOOM_OUT),
        ]:
            self._add_menu_item(submenu, caption, help, method, id = id or wx.ID_ANY)
        submenu.AppendSeparator()
        for caption, help, zoom, id in \
        [
            (_('Fit &width'),  _('Set magnification to fit page width'),  FitWidthZoom(), None),
            (_('Fit &page'),   _('Set magnification to fit page'),        FitPageZoom(),  wx.ID_ZOOM_FIT),
            (_('&Stretch'),    _('Stretch the image to the window size'), StretchZoom(),  None),
            (_('One &to one'), _('Set full resolution magnification.'),   OneToOneZoom(), wx.ID_ZOOM_100),
        ]:
            self._add_menu_item(submenu, caption, help, self.on_zoom(zoom), kind=wx.ITEM_RADIO, id = id or wx.ID_ANY)
        submenu.AppendSeparator()
        self.zoom_menu_items = {}
        for percent in 300, 200, 150, 100, 75, 50, 25:
            item = self._add_menu_item(
                submenu,
                '%d%%' % percent,
                _('Magnify %d%%') % percent,
                self.on_zoom(PercentZoom(percent)),
                kind=wx.ITEM_RADIO
            )
            if percent == 100:
                item.Check()
            self.zoom_menu_items[percent] = item
        menu.AppendMenu(wx.ID_ANY, _('&Zoom'), submenu)
        submenu = wx.Menu()
        for caption, help, method in \
        [
            (_('&Color') + '\tAlt+C', _('Display everything'),                                            self.on_display_everything),
            (_('&Stencil'),           _('Display only the document bitonal stencil'),                     self.on_display_stencil),
            (_('&Foreground'),        _('Display only the foreground layer'),                             self.on_display_foreground),
            (_('&Background'),        _('Display only the background layer'),                             self.on_display_background),
            (_('&None') + '\tAlt+N',  _('Neither display the foreground layer nor the background layer'), self.on_display_none)
        ]:
            self._add_menu_item(submenu, caption, help, method, kind=wx.ITEM_RADIO)
        menu.AppendMenu(wx.ID_ANY, _('&Image'), submenu)
        """
        submenu = wx.Menu()
        _tmp_items = []
        for caption, help, method in \
        [
            (_('&None'),                   _('Don\'t display non-raster data'),   self.on_display_no_nonraster),
            (_('&Hyperlinks') + '\tAlt+H', _('Display overprinted annotations'), self.on_display_maparea),
            (_('&Text') + '\tAlt+T',       _('Display the text layer'),          self.on_display_text),
        ]:
            _tmp_items += self._add_menu_item(submenu, caption, help, method, kind=wx.ITEM_RADIO),
        self._menu_item_display_no_nonraster, self._menu_item_display_maparea, self._menu_item_display_text = _tmp_items
        del _tmp_items
        self._menu_item_display_no_nonraster.Check()
        menu.AppendMenu(wx.ID_ANY, _('&Non-raster data'), submenu)
        """
        self._add_menu_item(menu, _('&Refresh') + '\tCtrl+L', _('Refresh the window'), self.on_refresh)
        return menu

    def do_percent_zoom(self, percent):
        self.page_widget.zoom = PercentZoom(percent)
        self.zoom_menu_items[percent].Check()

    def on_zoom_out(self, event):
        try:
            percent = self.page_widget.zoom.percent
        except ValueError:
            return # FIXME
        candidates = [k for k in self.zoom_menu_items.iterkeys() if k < percent]
        if not candidates:
            return
        self.do_percent_zoom(max(candidates))

    def on_zoom_in(self, event):
        try:
            percent = self.page_widget.zoom.percent
        except ValueError:
            return # FIXME
        candidates = [k for k in self.zoom_menu_items.iterkeys() if k > percent]
        if not candidates:
            return
        self.do_percent_zoom(min(candidates))


    def on_zoom(self, zoom):
        def event_handler(event):
            self.page_widget.zoom = zoom
        return event_handler

    def on_refresh(self, event):
        self.Refresh()

    def on_display_everything(self, event):
        self.page_widget.render_mode = djvu.decode.RENDER_COLOR

    def on_display_foreground(self, event):
        self.page_widget.render_mode = djvu.decode.RENDER_FOREGROUND

    def on_display_background(self, event):
        self.page_widget.render_mode = djvu.decode.RENDER_BACKGROUND

    def on_display_stencil(self, event):
        self.page_widget.render_mode = djvu.decode.RENDER_BLACK

    def on_display_none(self, event):
        self.page_widget.render_mode = None

    def on_char(self, event):
        key_code = event.GetKeyCode()
        if key_code == ord('-'):
            self.on_zoom_out(event)
        elif key_code == ord('+'):
            self.on_zoom_in(event)
        else:
            event.Skip()

WxDjVuMessage, wx.EVT_DJVU_MESSAGE = wx.lib.newevent.NewEvent()

class Context(djvu.decode.Context):

    def __new__(cls, window):
        return djvu.decode.Context.__new__(cls)

    def __init__(self, window):
        djvu.decode.Context.__init__(self)
        self.window = window

    def handle_message(self, message):
        wx.PostEvent(self.window, WxDjVuMessage(message=message))

 
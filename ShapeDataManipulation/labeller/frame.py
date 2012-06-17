# -*- coding: utf-8 -*-
'''
@author: Piotr Sikora
'''

import wx
import wx.lib.ogl
import wx.lib.newevent
import wx.lib.scrolledpanel


from hocr import DatahOCR
from labeller.context import ContextPanel
import shelve
import os.path

import djvusmooth.models.text


import djvu.decode
import djvu.const

from internal.frame import DjVuShapeToolsFrame

class hOCRLabeller(DjVuShapeToolsFrame):
    
    def __init__(self, *args, **kwargs):
        DjVuShapeToolsFrame.__init__(self, *args, **kwargs)

        wx.lib.ogl.OGLInitialize()

        self.data_hocr = DatahOCR()
        self.last_visited_directory = None
        self.context = Context(self)
        
        # menu - database
        menu = wx.Menu()
        self._add_menu_item(menu, 'Wybierz &Dokument', 'Wyświetla okno wyboru dokumentu z bazy', self.OnChooseDocument)
        self._add_menu_item(menu, text = 'Otwórz pliki z &hOCR', help = 'Wyświetla okno wybór plików zawierających dane hOCR', binding = self.OnLoadHOCR)
        self._add_menu_item(menu, '&Wyjście', 'Wyjdź z programu', binding = self.OnQuit)
        self.menubar.Append(menu, '&Dane')
        

        #tool = toolbar.AddLabelTool(wx.ID_ANY, 'Prz', wx.Bitmap('texit.png'))
        #TODO: make icons
        self.toolbar.Realize()

        self.SetSize((1024, 768))
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        panel = self.context_panel = ContextPanel(parent = self, data = self.data, data_hocr = self.data_hocr)
        
        mainSizer.Add(panel, 1, wx.EXPAND | wx.ALL, 1)
        panel = self.labelling_panel = wx.Panel(parent = self, )
        panel.SetBackgroundColour('#00ff00')
        mainSizer.Add(panel, 1, wx.EXPAND | wx.ALL, 1)
        panel = self.shapes_panel = wx.Panel(self)
        panel.SetBackgroundColour('#0000ff')
        mainSizer.Add(panel, 1, wx.EXPAND | wx.ALL, 1)
        
        self.SetSizer(mainSizer)

        #TODO: global binding of keystrokes
        self.context_panel.page_widget.Bind(wx.EVT_CHAR, self.on_char)

        self.Maximize()
        self.Centre()
        self.Show(True)
    
    def OnChooseDocument(self, event):
        self.choose_document()
    
    def OnLoadHOCR(self, event):
        self.load_hocr_data()
        
    def load_hocr_data(self):
        path = self.open_directory("Wybierz katalog z dokumentem i danymi hOCR")
        if path is not None:
            listing = os.listdir(path)
            for filename in listing:
                print(filename)
                if filename == self.data.current_document.name:
                    self.open_djvu_file(filename)
                else:
                    pass
            
    def open_djvu_file(self, filename):
        try:
            self.data_hocr.document = self.context.new_document(djvu.decode.FileURI(filename))
            self.data_hocr.text_model = TextModel(self.data_hocr.document)
            self.data_hocr.page_no = 0 # again, to set status bar text
            #self.update_title()
            self.context_panel.update_page_widget(new_document = True, new_page = True)
            self.context_panel.Refresh()
            self.context_panel.Update()
        except djvu.decode.JobFailed:
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

#DJVUSMOOTH code

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

class TextModel(djvusmooth.models.text.Text):

    def __init__(self, document):
        djvusmooth.models.text.Text.__init__(self)
        self._document = document

    def reset_document(self, document):
        self._document = document

    def acquire_data(self, n):
        text = self._document.pages[n].text
        text.wait()
        return text.sexpr    
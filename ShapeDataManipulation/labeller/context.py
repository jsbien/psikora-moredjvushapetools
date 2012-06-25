# -*- coding: utf-8 -*-
'''
@author: Piotr Sikora
'''

import wx
import wx.lib.scrolledpanel
from djvusmooth.gui.page import PageWidget, FitPageZoom
from djvusmooth.gui.page import RENDER_NONRASTER_TEXT

class ContextPanel(wx.lib.scrolledpanel.ScrolledPanel):
    
    def __init__(self, data, data_hocr, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)

        self.data = data
        self.data_hocr = data_hocr
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetupScrolling()
        self.page_widget = PageWidget(self)
        self.page_widget.render_nonraster = RENDER_NONRASTER_TEXT
        self.page_widget.zoom = FitPageZoom()
        sizer.Add(self.page_widget, 0, wx.ALL, 0)
        self.page = self.page_job = self.page_proxy = self.document_proxy = None
        self.Bind(wx.EVT_SIZE, self.page_widget.on_parent_resize)
        
        #self._page_text_callback = PageTextCallback(self)
        
    def update_page_widget(self, new_document = False, new_page = False):
        if self.data_hocr.document is None:
            self.page_widget.Hide()
            self.page = self.page_job = self.page_proxy = self.document_proxy = None
        elif self.page_job is None or new_page:
            self.page_widget.Show()
            self.page = self.data_hocr.current_page_djvu
            self.page_job = self.page.decode(wait = False)
            self.page_proxy = PageProxy(
                page = self.page,
                text_model = self.data_hocr.current_text_model,
                #annotations_model = self.annotations_model[self.page_no]
            )
            #self.page_proxy.register_text_callback(self._page_text_callback)
            if new_document:
                self.document_proxy = DocumentProxy(document = self.data_hocr.document, 
                                                    #outline = self.outline_model
                                                    )
        self.page_widget.page = self.page_proxy
        #self.text_browser.page = self.page_proxy
        
    def OnChildFocus(self, event):
        # We *don't* want to scroll to the child window which just got the focus.
        # So just skip the event:
        event.Skip()
        

            
class PageProxy(object):
    def __init__(self, page, text_model, annotations_model = None):
        self._page = page
        self._text = text_model
        self._annotations = annotations_model

    @property
    def page_job(self):
        return self._page.decode(wait = False)

    @property
    def text(self):
        return self._text

    @property
    def annotations(self):
        return self._annotations

    def register_text_callback(self, callback):
        self._text.register_callback(callback)

    def register_annotations_callback(self, callback):
        self._annotations.register_callback(callback)
        
class DocumentProxy(object):

    def __init__(self, document, outline = None):
        self._document = document
        self._outline = outline

    @property
    def outline(self):
        return self._outline

    def register_outline_callback(self, callback):
        self._outline.register_callback(callback)

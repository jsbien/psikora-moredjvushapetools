'''
@author: Piotr Sikora
'''

import djvusmooth.models.text

class DatahOCR:
    
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.document = None
        self.hocr_pages = {}
        
        self.text_model = None
        
    def add_page(self, page_no, hocr_page):
        self.hocr_pages[page_no] = hocr_page
     
    def make_text_model(self, callbacks = []):
        self.text_model = TextModel(self.document, self.hocr_pages, callbacks) 
       
    def get_line_text(self):
        return self.text_model.get_text()

    def _get_page_no(self):
        return self.text_model.current_page
    
    page_no = property(_get_page_no)
    
    def _get_current_text_model(self):
        return self.text_model[self.page_no]
    current_text_model = property(_get_current_text_model)    

    def _get_current_page_djvu(self):
        return self.document.pages[self.page_no - 1]
    current_page_djvu = property(_get_current_page_djvu)    

    
class TextModel(djvusmooth.models.text.Text):

    def __init__(self, document, pages_data, callbacks = []):
        djvusmooth.models.text.Text.__init__(self)
        self._document = document
        self._pages_data = pages_data
        self._current_page = min(self._pages_data.keys())
        self._current_line = 0
        self._callbacks = callbacks

    def reset_document(self, document, pages_data):
        self._document = document
        self._pages_data = pages_data

    def acquire_data(self, n):
        #text = self._document.pages[n].text
        #text.wait()
        #return text.sexpr
        return self._pages_data[n] # to account for pages being numbered from 1, unlike arrays

    def next_page(self):
        greater_pages = [
                       page_no
                       for page_no in self._pages_data.keys()
                       if page_no > self._current_page
                       ]
        if greater_pages:
            self.current_page = min(greater_pages)
            self.current_line = 0
    
    def prev_page(self):
        lesser_pages = [
                       page_no
                       for page_no in self._pages_data.keys()
                       if page_no < self._current_page
                       ]
        if lesser_pages:
            self.current_page = max(lesser_pages)
            self.current_line = len(self[self.current_page].lines) - 1
    
    def next_line(self):
        self.current_line += 1 
        
    def prev_line(self):
        self.current_line -= 1
    
    def get_text(self):
        return self[self.current_page].get_current_node().text
        #return "Text"
    
    def _get_current_line(self):
        return self._current_line
    def _set_current_line(self, value):
        if value < 0:
            self.prev_page()
        elif value >= len(self[self.current_page].lines):
            self.next_page()
        else:
            self._current_line = value
        self[self.current_page].current_line = self._current_line
    current_line = property(_get_current_line, _set_current_line)

    def _get_current_page(self):
        return self._current_page
    def _set_current_page(self, value):
        if value not in self._pages_data.keys():
            raise ValueError("Setting current page to one with nonexistent hocr data")
        self._current_page = value
        for callback in self._callbacks:
            callback.notify_page_change()
    current_page = property(_get_current_page, _set_current_page)


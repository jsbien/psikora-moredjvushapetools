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
     
    def make_text_model(self):
        self.text_model = TextModel(self.document, self.hocr_pages) 
       
    def get_line_text(self):
        return self.text_model.get_text()
       
class TextModel(djvusmooth.models.text.Text):

    def __init__(self, document, page_data):
        djvusmooth.models.text.Text.__init__(self)
        self._document = document
        self._page_data = page_data
        self._current_page = 0
        self._current_line = 0

    def reset_document(self, document, page_data):
        self._document = document
        self._page_data = page_data

    def acquire_data(self, n):
        text = self._document.pages[n].text
        text.wait()
        return text.sexpr
        #return self._page_data[n + 1] # to account for pages being numbered from 1, unlike arrays
    
    def next_line(self):
        self.current_line += 1 
        
    def prev_line(self):
        self.current_line -= 1
    
    def get_text(self):
        return self[self.current_page].get_current_node().text
    
    def get_current_line(self):
        return self._current_line
    def set_current_line(self, value):
        self._current_line = value
        self[self.current_page].current_line = value
        if self._current_line < 0:
            self.current_page -= 1
            self._current_line = 0
    current_line = property(get_current_line, set_current_line)

    def get_current_page(self):
        return self._current_page
    def set_current_page(self, value):
        self._current_page = value
    current_page = property(get_current_page, set_current_page)

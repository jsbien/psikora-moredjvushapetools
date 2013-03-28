# -*- coding: utf-8 -*-
'''
    hOCR Labeller of DjVu shapes    
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

import djvusmooth.models.text
import djvu.const
from operator import itemgetter, attrgetter


from utils import Rect, log

class DatahOCR:
    
    def __init__(self, data):
        self.data = data
        self.clear()
        
    def clear(self):
        self.document = None
        self.hocr_pages = {}
        self.text_model = None
        
        self._nodes_to_shapes = {}
        
        self._page_range = None
        self._page_no_mod = None
        
    def add_page(self, page_no, hocr_page):
        self.hocr_pages[page_no] = hocr_page
     
    def make_text_model(self, callbacks = []):
        self.text_model = TextModel(self.document, self, callbacks) 
        self._find_shapes_for_nodes()
        self.data.load_labels()
        self.data.compute_hierarchies()
        self.text_model.current_char = 0
        
    
    def _find_shapes_for_nodes(self):
        for page_no in self.hocr_pages.keys():
            if self.hocr_pages[page_no] is not None:
                self._find_shapes_for_nodes_by_page(page_no)
        
                
    def _find_shapes_for_nodes_by_page(self, page_no):
        translated_page_no = self._page_no_translation(page_no)
        shapes = []
        if translated_page_no in self.data.pages.keys(): #get_inherited dictionary
            shapes += self.data.db_manipulator.fetch_shapes(self.data.pages[translated_page_no])
        for dictionary in self.data.shape_dictionaries:
            if dictionary.page == translated_page_no:
                shapes += self.data.db_manipulator.fetch_shapes(dictionary.db_id)
        self.data.add_shapes(shapes)
        #page_dictionaries = self.data.db_manipulator.fetch_dictionaries_for_page(self.data.current_document.db_id, self._page_no_translation(page_no))
        self.data.add_blits(self.data.db_manipulator.fetch_blits(self.data.current_document.db_id, translated_page_no), translated_page_no)
            
        blit_rects = []
        for blit in self.data.blits[translated_page_no]:
            rect = Rect(blit.x, blit.y, blit.w, blit.h)
            rect.shape = blit.shape
            blit_rects.append(rect)
        #for node in self.hocr_pages[translated_page_no].chars:
        for node in self.text_model[translated_page_no].chars:
            node_rect = Rect(*node.rect)
            for blit_rect in blit_rects:
                if node_rect.intersect(blit_rect):
                    node.shapes.append(blit_rect.shape)
                    node.blits.append(blit_rect)
        for node in self.text_model[translated_page_no].lines:
            node_rect = Rect(*node.rect)
            for blit_rect in blit_rects:
                if node_rect.intersect(blit_rect):
                    #node.shapes.append(blit_rect.shape)
                    node.blits.append(blit_rect)
                    
    def next_shape(self, previous = False, find_unlabeled = False):
        if previous:
            direction = -1
        else:
            direction = 1
        while True:
            self.text_model.current_char += direction 
            if not find_unlabeled or self.data.current_shape.label is None or self.text_model.at_limit:
                break
       
    def get_line_text(self):
        return self.text_model.get_line_text()

    def get_line_rect(self):
        node = self.text_model[self.text_model.current_page].current_line_node
        rect = Rect(node.x, node.y, node.w, node.h)
        return rect
    
    def get_char_rect(self):
        node = self.text_model[self.text_model.current_page].current_char_node
        rect = Rect(node.x, node.y, node.w, node.h)
        return rect
    
    def get_line_blits(self):
        return self.text_model[self.text_model.current_page].current_line_node.blits

    def _get_page_no(self):
        return self.text_model.current_page
    page_no = property(_get_page_no)
    
    def _get_current_text_model(self):
        return self.text_model[self.page_no]
    current_text_model = property(_get_current_text_model)    

    def _get_current_page_djvu(self):
        return self.document.pages[self._page_no_translation(self.page_no)]
    current_page_djvu = property(_get_current_page_djvu)    

    def _page_no_translation(self, page_no):
        return page_no + self.page_no_mod
    
    def _page_no_mod(self):
        if self._page_no_mod is None:
            if self.page_range[0] > 0 and self.page_range[1] == len(self.document.pages):
                self._page_no_mod = -1
            else:
                self._page_no_mod = 0
        return self._page_no_mod
    page_no_mod = property(_page_no_mod)
    
    def _get_page_range(self):
        if self._page_range is None:
            low = min(self.hocr_pages.keys())
            high = max(self.hocr_pages.keys())
            self._page_range = (low, high)
        return self._page_range
    page_range = property(_get_page_range)
    
class TextModel(djvusmooth.models.text.Text):

    def __init__(self, document, data_hocr, callbacks = []):
        self._document = document
        self.data_hocr = data_hocr
        self.data = data_hocr.data
        self._pages_data = data_hocr.hocr_pages
        self._current_page = [
                              page_no
                              for page_no in sorted(self._pages_data.keys()) 
                              if self._pages_data[page_no] is not None
                              ][0]
        self._current_line = 0
        self._current_char = 0
        self._total_chars = 0
        self._callbacks = callbacks
        djvusmooth.models.text.Text.__init__(self)
        self.at_limit = True

    def reset_document(self, document, pages_data):
        self._document = document
        self._pages_data = pages_data

    def acquire_data(self, n):
        return self._pages_data[n]

    def next_page(self):
        greater_pages = [
                       page_no
                       for page_no in self._pages_data.keys()
                       if page_no > self._current_page and self._pages_data[page_no] is not None
                       ]
        if greater_pages:
            self.current_page = min(greater_pages)
            self.current_line = 0
        else:
            self.at_limit = True
    
    def prev_page(self):
        lesser_pages = [
                       page_no
                       for page_no in self._pages_data.keys()
                       if page_no < self._current_page and self._pages_data[page_no] is not None
                       ]
        if lesser_pages:
            self.current_page = max(lesser_pages)
            self.current_line = len(self[self.current_page].lines) - 1
        else:
            self.at_limit = True
    
    def next_line(self, character_shift = 0):
        current_line = self.current_line
        self.current_line += 1
        if self.current_line != current_line:
            self.current_char = character_shift
        
    def _current_line_len(self):
        return len(list(self[self.current_page].current_line_node.get_leafs()))    
    current_line_len = property(_current_line_len)
    
    def _get_current_char_node(self):
        return self[self.current_page].current_char_node
    current_char_node = property(_get_current_char_node)
    
    def prev_line(self, character_shift = 0):
        current_line = self.current_line
        self.current_line -= 1
        if self.current_line != current_line:
            self.current_char = self.current_line_len - 1 + character_shift 
    
    def get_line_text(self):
        return ''.join([
                 node.text + ' '
                 for node in iter(self[self.current_page].current_line_node)
                 ])

    def get_char_text(self):
        return self[self.current_page].current_char_node.text
    
    def get_current_char_position(self):
        nodes = self[self.current_page].current_line_node.get_postorder_nodes()
        pos = 0
        current_node = self[self.current_page].current_char_node
        for node in nodes:
            if node == current_node:
                return (pos, pos + len(node.text))
            elif node.type == djvu.const.TEXT_ZONE_WORD :
                pos += 1
            elif node.type == djvu.const.TEXT_ZONE_CHARACTER:
                pos += len(node.text)
        return None

    def select_shape(self, node):
        if not node.shape_selected:
            node_rect = Rect(*node.rect)
            shapes_by_coverage_and_size = {}
            for i in range(len(node.shapes)):
                blit = node.blits[i]
                shapes_by_coverage_and_size[(blit.coverage_percent(node_rect), blit.size)] = (node.shapes[i], blit)
            shapes = []
            blits = []
            for shape_key in sorted(shapes_by_coverage_and_size.keys(), key=itemgetter(0,1), reverse = True):
                shapes.append(shapes_by_coverage_and_size[shape_key][0])
                blits.append(shapes_by_coverage_and_size[shape_key][1])
            node.shapes = shapes
            node.blits = blits
            node.shape_selected = True
        return node.shapes[0]
    
    def _get_current_char(self):
        return self._current_char
    def _set_current_char(self, value):
        total_line_chars = len(list(self[self.current_page].current_line_node.get_leafs()))
        if value < 0:
            self.prev_line(value)
        elif value >= total_line_chars:
            self.next_line(value - total_line_chars)
        else:
            self._current_char = value
            self.at_limit = False
        self[self.current_page].current_char = self._current_char
        if self[self.current_page].current_char_node.shapes:
            self.data.current_shape = self.select_shape(self[self.current_page].current_char_node)
           # print("Current hOCR node intersects with " + str(len(self[self.current_page].current_char_node.shapes)) + " shapes")
            self.data.select_hierarchy_for_current_shape() #TODO: needs to handle multiple shapes
        else:
            self.data.current_shape = None
            self.data.current_hierarchy = None
    current_char = property(_get_current_char, _set_current_char)
    
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
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

import Image

class Document:
    def __init__(self, db_id, name, address):
        self.db_id = db_id
        self.name = name
        self.address = address

class ShapeDictionary:
    def __init__(self, db_id, name, page):
        self.db_id = db_id
        self.name = name
        self.page = page
    
    def is_inherited(self):
        return self.page == -1
        
class Blit:
    
    def __init__(self, blit_data):
        self.db_id, self.doc_id, self.page_number, self.shape_id, self.b_left, self.b_bottom = blit_data
        self.w = None
        self.h = None
        self.shape = None
        
    def get_x(self):
        return self.b_left
    x = property(get_x) 
    
    def get_y(self):
        return self.b_bottom
    y = property(get_y)
        
    def __str__(self):
        return "Blit " + str(self.db_id) + " from doc: " + str(self.doc_id) + " page: " + str(self.page_number) + \
            " of shape: " + str(self.shape_id) + " at: " + str(self.b_left) + ', ' + str(self.b_bottom)
        
        
class BoundingBox:
    def __init__(self, top, left, right, bottom):            
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        
class Shape:
    
    def __init__(self, shape_data):
        db_id, original_id, parent_id, bits, width, height, dict_id, bbox_top, bbox_left, bbox_right, bbox_bottom = shape_data
        self.db_id = db_id
        self.id = original_id
        self.parent_db_id = parent_id
        self.parent = None
        self.children = []
        self.bits = bits
        self.width = width
        self.height = height
        self.size = (width, height)
        self.bounding_box = BoundingBox(bbox_top,bbox_left,bbox_right,bbox_bottom)
        self._image = None
        self.label = None
        
        self.blit_count = 0
        self.hierarchy_max_size = None

    def has_no_parent(self):
        return self.parent_db_id == -1

    def _get_image(self):
        if self._image == None:
            self._image = self._decode_image()
        return self._image
    image = property(_get_image)

    def _decode_image(self):
        def behead(pbm, width, height):
            ''' 
            GUTF8String head;
            head.format("P%c\n%d %d\n", (raw ? '4' : '1'), ncolumns, nrows);
            bs.writall((void*)(const char *)head, head.length());
            '''
            #
            bytes_to_eliminate = 5 + len(str(width)) + len(str(height))
            return pbm[bytes_to_eliminate:]
        imagebits = behead(self.bits, self.width, self.height)
        return Image.fromstring("1", self.size, imagebits, "raw", "1;I", 0, 1)
    
    def count_descendants(self):
        return self.hierarchy_count - 1

    def _get_hierarchy_count(self):
        count = 1 #count self
        for child in self.children:
            count += child.hierarchy_count
        return count
    hierarchy_count = property(_get_hierarchy_count)

    def get_hierarchy_size(self):
        if self.hierarchy_max_size is None:
            max_width, max_height = self.width, self.height
            for child in self.children:
                child_width, child_height = child.get_hierarchy_size()
                if child_width > max_width:
                    max_width = child_width
                if child_height > max_height:
                    max_height = child_height
            self.hierarchy_max_size = (max_width, max_height)
        return self.hierarchy_max_size

    def linearise_hierarchy(self):
        linearised_hierarchy = []
        linearised_hierarchy.append(self)
        for child in self.children:
            linearised_hierarchy.extend(child.linearise_hierarchy())
        return linearised_hierarchy
    
    def hierarchy_height(self):
        max_height = 0
        for child in self.children:
            if child.hierarchy_height() + 1 > max_height:
                max_height = child.hierarchy_height() + 1
        return max_height
    
    def hierarchy_depth(self):
        depth = 0
        current_shape = self
        while current_shape.parent is not None:
            depth += 1
            current_shape = current_shape.parent 
        return depth
    
    def isAncestorOf(self, shape):
        current_shape = shape
        while current_shape.parent is not None:
            if current_shape.parent == self:
                return True
            current_shape = current_shape.parent 
        return False
    
    def isDescendantOf(self, shape):
        return shape.isAncestorOf(self)     
    
    def max_width(self):
        childwidth = 0
        for child in self.children:
            childwidth += child.max_width()
        if childwidth > 1:
            return childwidth
        else:
            return 1

    def _get_hierarchy(self):
        hierarchy_root = self
        return hierarchy_root
    hierarchy = property(_get_hierarchy)

class Label:
    
    def __init__(self, font_id, font, font_type_id, font_type, font_size_id, font_size, textel_type, textel_ids = None, textel = None, noise = False):
        self.font_id = font_id 
        self.font = font
        self.font_type_id = font_type_id
        self.font_type = font_type
        self.font_size_id = font_size_id
        self.font_size = font_size              
        self.textel_ids = textel_ids
        self.textel = textel
        self.textel_type = textel_type
        self.db_id = None
        self.noise = noise
        
    def __str__(self):
        if self.textel is not None:
            return str(self.textel)
        else:
            return ''
        
        
class UnicodeChar:
    
    def __init__(self, db_id, character, name):
        self.db_id = db_id
        self.character = character
        self.name = name   
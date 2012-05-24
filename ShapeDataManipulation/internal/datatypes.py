'''

@author: Piotr Sikora
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
        self.image = None
        
        self.hierarchy_count = None
        self.hierarchy_max_size = None

    def has_no_parent(self):
        return self.parent_db_id == -1

    def get_image(self):
        if self.image == None:
            self.image = self.decode_image()
        return self.image

    def decode_image(self):
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
        if self.hierarchy_count is None:
            count = 1 #count self
            for child in self.children:
                count += child.count_descendants()
            count += len(self.children)
            self.hierarchy_count = count 
        return self.hierarchy_count - 1

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
    
    def depth(self):
        max_depth = 1
        for child in self.children:
            if child.depth() + 1 > max_depth:
                max_depth = child.depth() + 1
        return max_depth
    
    def hierarchyheight(self):
        height = 1
        current_shape = self
        while current_shape.parent is not None:
            height += 1
            current_shape = current_shape.parent 
        return height
    
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
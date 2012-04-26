'''

@author: Piotr Sikora
'''

import Image

class Document:
    def __init__(self, db_id, name):
        self.db_id = db_id
        self.name = name

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
        count = 0
        for child in self.children:
            count += child.count_descendants()
        count += len(self.children)
        return count

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
    
    def max_width(self):
        childwidth = 0
        for child in self.children:
            childwidth += child.max_width()
        if childwidth > 1:
            return childwidth
        else:
            return 1
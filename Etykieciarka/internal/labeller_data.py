'''
Created on Apr 17, 2012

@author: zasvid
'''

class LabellerData():
    
    def __init__(self):
        self.documents = []
        self.current_document = None
        self.shape_dictionaries = []
        self.current_dictionary = None
        self.shape_hierarchies = []
        self.current_shape_hierarchy = None
        self.shapes = []
        self.shape_translation = {}
        self.current_shape = None
        
    def fill_shape_dicitonary(self, shapes):
        self.shapes = shapes
        for i in range(len(self.shapes)):
            shape = self.shapes[i]
            self.shape_translation[shape.db_id] = shape   
        self.compute_hierarchies()
        
    def compute_hierarchies(self):
        self.shape_hierarchies = []
        self.current_shape_hierarchy = None
        for shape in self.shapes:
            if shape.has_no_parent():
                self.shape_hierarchies.append(shape)
            else:
                shape.parent = self.shape_translation[shape.parent_db_id]
                shape.parent.children.append(shape)
    
    
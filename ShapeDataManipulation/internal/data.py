'''
@author: Piotr Sikora
'''

class ShapeData:
    
    def __init__(self):
        self.documents = []
        self.current_document = None
        self.hocr_pages = {}
        self.shape_dictionaries = []
        self.current_dictionary = None
        self.shape_hierarchies = []
        self.hierarchy_sorting_method = None
        self.current_shape_hierarchy = None
        self.shapes = []
        self.shape_translation = {}
        self.current_shape = None
        
    def fill_shape_dictionary(self, shapes):
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
        self.hierarchy_sorting_method = None
        
    def sorted_hierarchies(self, sorting_method):
        if self.hierarchy_sorting_method != sorting_method:
            self.hierarchy_sorting_method = sorting_method
            if sorting_method is None:
                self.shape_hierarchies.sort(key = lambda hierarchy: hierarchy.db_id)
            elif sorting_method == 'count':
                self.shape_hierarchies.sort(key = lambda hierarchy: hierarchy.count_descendants(), reverse = True)
            elif sorting_method == 'size':
                self.shape_hierarchies.sort(key = lambda hierarchy: hierarchy.get_hierarchy_size()[0] * hierarchy.get_hierarchy_size()[1], reverse = True)
        return self.shape_hierarchies
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

from internal.datatypes import Label, UnicodeChar

class ShapeData:
    
    def __init__(self):#, labelling = False
        #self.labelling = labelling
        self._db_manipulator = None
        self.documents = []
        self.current_document = None
        self.hocr_pages = {}
        self.shape_dictionaries = []
        self.pages = {}
        self.shapes = {}
        self.current_shape = None
        
        #browser data
        self.current_dictionary = None
        self.shape_hierarchies = []
        self.hierarchy_sorting_method = None
        self.current_hierarchy = None
        
        #labeller data
        self.textel_types = ['tekstel właściwy', 'mikrotekstel', 'makrotekstel' ]
        self.blits = {}
        self.labels = {} #ID : Label
        self.unicode_chars = {} # char: UnicodeChar
        self.uchars_by_id = {}
        self.clear()
        
    def clear(self):
        self._fonts = None #ID : string
        self._font_sizes = None #ID : string
        self._font_types = None
        self._users = None #ID : string
        self._font_ids = {} #string : ID
        self._font_size_ids = {} #string : ID
        self._font_type_ids = {} #string : ID
        self._user_ids = {} #string : ID
        
    def _get_fonts(self):
        if self._fonts is None:
            self._fonts = self.db_manipulator.fetch_simple("fonts")
        return self._fonts
    fonts = property(_get_fonts)
    
    def _get_font_sizes(self):
        if self._font_sizes is None:
            self._font_sizes = self.db_manipulator.fetch_simple("font_sizes")
        return self._font_sizes
    font_sizes = property(_get_font_sizes)

    def _get_font_types(self):
        if self._font_types is None:
            self._font_types = self.db_manipulator.fetch_simple("font_types")
        return self._font_types
    font_types = property(_get_font_types)
    
    def _get_users(self):
        if self._users is None:
            self._users = self.db_manipulator.fetch_simple("labeller_users")
        return self._users
    users = property(_get_users)
    
    def user_id(self, username):
        if username in self._user_ids.keys():
            return self._user_ids[username]
        else:
            if username in self.users.values():
                for key in self.users.keys():
                    if self.users[key] == username:
                        self._user_ids[username] = key
                        return key 
            else:
                if username == self.db_manipulator.db_user:
                    user_id = self.db_manipulator.insert_simple("labeller_users", "username", username)
                    self.users[user_id] = username
                    return user_id
                else:
                    raise ValueError
        
    def uchar_id(self, uchar, ucharname):
        if uchar in self.unicode_chars:
            return self.unicode_chars[uchar].db_id
        else:
            uchar_id =  self.db_manipulator.insert_uchar(uchar, ucharname)
            uchar_obj = UnicodeChar(uchar_id, uchar, ucharname)
            self.unicode_chars[uchar] = uchar_obj
            self.uchars_by_id[uchar_id] = uchar_obj
            return uchar_id
       
    def _get_db_manipulator(self):
        return self._db_manipulator
    def _set_db_manipulator(self, value):
        #self._db_manipulator = value
        pass
    db_manipulator = property(_get_db_manipulator, _set_db_manipulator)    
   
    def clear_shapes(self):
        self.shapes = {}
    
    def add_shapes(self, shapes):    
        for shape in shapes:
            self.shapes[shape.db_id] = shape   

    def fill_shape_dictionary(self, shapes):
        self.shapes = {}
        self.add_shapes(shapes)
        self.compute_hierarchies()
        
    def compute_hierarchies(self):
        self.shape_hierarchies = []
        self.current_hierarchy = None
        for shape in self.shapes.values():
            if shape.has_no_parent():
                self.shape_hierarchies.append(shape)
            else:
                shape.parent = self.shapes[shape.parent_db_id]
                shape.parent.children.append(shape)
        self.hierarchy_sorting_method = None
        
    def select_hierarchy_for_current_shape(self):
        self.current_hierarchy = self._hierarchy_for_shape(self.current_shape) 
   
    def _hierarchy_for_shape(self, shape):
        if shape.parent is None:
            return shape
        else:
            return self._hierarchy_for_shape(shape.parent)
    
    def sorted_hierarchies(self, sorting_method):
        #if self.hierarchy_sorting_method != sorting_method:
        if True:
            #self.hierarchy_sorting_method = sorting_method
            if sorting_method is None:
                self.shape_hierarchies.sort(key = lambda hierarchy: hierarchy.db_id)
            elif sorting_method == 'count':
                self.shape_hierarchies.sort(key = lambda hierarchy: hierarchy.count_descendants(), reverse = True)
            elif sorting_method == 'size':
                self.shape_hierarchies.sort(key = lambda hierarchy: hierarchy.get_hierarchy_size()[0] * hierarchy.get_hierarchy_size()[1], reverse = True)
        return self.shape_hierarchies
    
    def cut_out(self, shape):
        parent = shape.parent
        if parent is not None:
            parent_id = parent.db_id
        else:
            parent_id = -1 
        self.cut_off(shape)
        for child in shape.children:
            child.parent = parent
            child.parent_db_id = parent_id
            if parent is not None:
                parent.children.append(child)
            else:
                self.shape_hierarchies.append(child)
                if shape.label is not None:
                    #clone label for a new hierarchy
                    self._clone_label_for_shapes(shape.label, child.linearise_hierarchy()) 
            self.db_manipulator.shape_edit(shape_id = child.db_id,
                                           prev_parent_id = shape.db_id,
                                           new_parent_id = parent_id,
                                           user_id = self.user_id(self.db_manipulator.db_user))
        shape.children = []
        self.db_manipulator.commit()
        
    def cut_off(self, shape):
        if shape.parent is not None:
            shape.parent.children.remove(shape)
            parent_db_id = shape.parent_db_id
            shape.parent = None
            shape.parent_db_id = -1
            self.shape_hierarchies.append(shape)
            self.db_manipulator.shape_edit(shape_id = shape.db_id, prev_parent_id = parent_db_id, new_parent_id = -1, user_id = self.user_id(self.db_manipulator.db_user))
            if shape.label is not None:
                self._clone_label_for_shapes(shape.label, shape.linearise_hierarchy())
            self.db_manipulator.commit()

    def _clone_label_for_shapes(self, label, shapes):
        #clone the label
        cloned_label = Label(font_id = label.font_id, font = label.font,
                      font_type_id = label.font_type_id, font_type = label.font_type,
                      font_size_id = label.font_size_id, font_size = label.font_size,
                      textel_ids = label.textel_ids, textel = label.textel, 
                      textel_type = label.textel_type, noise = label.noise 
                      )
        cloned_label.db_id = self.db_manipulator.insert_label(cloned_label, self.user_id(self.db_manipulator.db_user), self.current_document.db_id)
        #save a link between label and uchars
        for sequence in range(len(cloned_label.textel_ids)):
            self.db_manipulator.insert_into_junction(table = "label_chars", fields = ("sequence", "uchar_id","label_id"), values = (sequence, cloned_label.textel_ids[sequence], cloned_label.db_id))
        #label the hierarchy of shapes
        for sh in shapes:
            self.db_manipulator.update_junction(table = "labelled_shapes", updated_field = "label_id", other_field = "shape_id", new_value = cloned_label.db_id, previous_value = label.db_id, other_value = sh.db_id)
            sh.label = cloned_label

    def add_blits(self, blits, page_no):
        for blit in blits:
            shape = self.shapes[blit.shape_id]
            shape.blit_count += 1
            blit.w = shape.bounding_box.right
            blit.h = shape.bounding_box.top
            blit.shape = shape
        self.blits[page_no] = blits
        
    def load_labels(self, only_current_dictionary = False):
        labels_to_uchars = self.db_manipulator.fetch_junction_table(table = "label_chars", selection = "label_id, uchar_id")
        
        raw_label_data = self.db_manipulator.fetch_labels_raw_data(self.current_document.db_id)
        labels = {}
        for db_id, font_id, font_size_id, font_type_id, textel_type, _, _, _, noise in raw_label_data: #document id is known, user and date ignored
            font = self.fonts.get(font_id, None)
            font_type = self.font_types.get(font_type_id, None)
            font_size = self.font_sizes.get(font_size_id, None)
            uchar_ids = labels_to_uchars.get(db_id, [])
            unicode_characters = [self.uchars_by_id[uchar_id] for uchar_id in uchar_ids]
            label = Label(font_id = font_id, font = font,
                      font_type_id = font_type_id, font_type = font_type,
                      font_size_id = font_size_id, font_size = font_size,              
                      textel_ids = uchar_ids, textel = ''.join([uchar.character for uchar in unicode_characters]), 
                      textel_type = textel_type, noise = noise
                      )
            label.db_id = db_id
            labels[db_id] = label
        labels_to_shapes = self.db_manipulator.fetch_junction_table("labelled_shapes")
        
        for label in labels.values():
            shape_ids = labels_to_shapes.get(label.db_id, [])
            for shape_id in shape_ids:
                shape = self.shapes.get(shape_id, None)
                if shape is not None: 
                    shape.label = label 
                else:
                    if not only_current_dictionary:
                        print("Shape missing for label: " + str(label.db_id)) #TODO: put some real error handling here
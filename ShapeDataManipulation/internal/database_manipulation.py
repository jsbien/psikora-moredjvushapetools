'''
@author: Piotr Sikora
'''

import MySQLdb as mdb
from datatypes import *


class DatabaseManipulator:
    
    def __init__(self, db_name, db_host, db_user, db_pass, labelling = True):
        self.db_name = db_name
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.connection = mdb.connect(db_host, db_user, db_pass, db_name)
        with self.connection:
            self.cursor = self.connection.cursor()
            if labelling:
                self.prepare_database_for_labelling()
    
    def close(self):  
        print("Closing connection!")      
        self.connection.close()
    
    def fetch_documents(self):
        self.cursor.execute("SELECT * FROM documents")
        documents_data = self.cursor.fetchall()
        documents = []
        for db_id, name, address in documents_data:
            documents.append(Document(db_id, name, address)) 
        return documents
    
    def fetch_dictionaries(self, document_id):
        self.cursor.execute("SELECT * FROM dictionaries WHERE document_id = "+ str(document_id))
        data = self.cursor.fetchall()
        dictionaries = []
        for db_id, name, page, _ in data:
            dictionaries.append(ShapeDictionary(db_id, name, page))
        return dictionaries
        
    def fetch_pages(self, document_id):
        self.cursor.execute("SELECT * FROM pages WHERE document_id = "+ str(document_id))
        data = self.cursor.fetchall()
        pages = {}
        for _, inh_dict_id, page in data:
            pages[page] = inh_dict_id
        return pages
    
    def fetch_shapes(self, dictionary_id):
        """ Fetches shapes from a single dictionary
        """
        self.cursor.execute("SELECT * FROM shapes WHERE dictionary_id = "+str(dictionary_id))
        data = self.cursor.fetchall()
        shapes = []
        for shape_data in data:
            shapes.append(Shape(shape_data))
        return shapes
    
    def prepare_database_for_labelling(self):
        self.cursor.execute("SHOW TABLES LIKE 'labels'")
        if self.cursor.fetchone() is None:
            create_command = "create table labels(" \
                            "id INT not null auto_increment primary key, " \
                            "font varchar(60) not null, " \
                            "font_size varchar(60) not null, " \
                            "user VARCHAR(60) not null, " \
                            "date DATETIME " \
                            ")"
            self.cursor.execute(create_command)
        self.cursor.execute("SHOW TABLES LIKE 'labelled_shapes'")
        if self.cursor.fetchone() is None:
            create_command = "create table labelled_shapes(" \
                            "label_id INT not null, " \
                            "shape_id INT not null " \
                            ")"
            self.cursor.execute(create_command)
        self.cursor.execute("SHOW TABLES LIKE 'label_chars'")
        if self.cursor.fetchone() is None:
            create_command = "create table label_chars(" \
                            "label_id INT not null, " \
                            "uchar_id INT not null " \
                            ")"
            self.cursor.execute(create_command)
        self.cursor.execute("SHOW TABLES LIKE 'unicode_chars'")
        if self.cursor.fetchone() is None:
            #create_command = "create table unicode_chars(" \
             #               "label_id INT not null, " \
              #              "uchar_id INT not null, " \
               #             ")"
            #self.cursor.execute(create_command)
            print("Unicode char table not ready.")
            #TODO: what to put in the unicode chars table
        self.cursor.execute("SHOW TABLES LIKE 'shape_edits'")
        if self.cursor.fetchone() is None:
            create_command = "create table shape_edits(" \
                            "id INT not null auto_increment primary key, " \
                            "shape_id INT not null, " \
                            "prev_parent INT not null, " \
                            "new_parent INT not null, " \
                            "user VARCHAR(60) not null, " \
                            "date DATETIME " \
                            ")"
            self.cursor.execute(create_command)

    def shape_edit(self, shape_id, prev_parent_id, new_parent_id):
        query = "UPDATE shapes SET parent_id = " + str(new_parent_id) + " WHERE id = " + str(shape_id)
        self.cursor.execute(query)
        query = "INSERT INTO shape_edits(user, shape_id, prev_parent, new_parent, date) VALUES('" \
                + str(self.db_user)+"', " + str(shape_id) + ", " + str(prev_parent_id) + ", " + str(new_parent_id) + ", now())"
        self.cursor.execute(query)
        #TODO: datetime

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
    
    def fetch_blits(self, document_id, page_no):
        self.cursor.execute("SELECT * FROM blits WHERE document_id = " + str(document_id) + " AND page_number = " + str(page_no))
        data = self.cursor.fetchall()
        blits = []
        for blit_data in data:
            blits.append(Blit(blit_data))
        return blits
    
    def fetch_simple(self, table):
        self.cursor.execute("SELECT * from " + str(table))
        data = self.cursor.fetchall()
        processed_data = {}
        for db_id, field in data:
            processed_data[db_id] = field
        return processed_data
    
    def reset_database_for_labelling(self):
        self.cursor.execute("DROP TABLE IF EXISTS labels")
        self.cursor.execute("DROP TABLE IF EXISTS shape_edits")
        self.cursor.execute("DROP TABLE IF EXISTS labelled_shapes")
        self.cursor.execute("DROP TABLE IF EXISTS label_chars")
    
    def prepare_database_for_labelling(self):
        self.cursor.execute("SHOW TABLES LIKE 'labels'")
        if self.cursor.fetchone() is None:
            create_command = "create table labels(" \
                            "id INT not null auto_increment primary key, " \
                            "font INT not null, " \
                            "font_size INT not null, " \
                            "user INT not null, " \
                            "date DATETIME " \
                            ")"
            self.cursor.execute(create_command)
        else:
            command = "SHOW COLUMNS FROM labels LIKE 'font'"
            self.cursor.execute(command)
            if self.cursor.fetchone()[1] == 'varchar(60)':
                self.reset_database_for_labelling()
                print(str("Labelling tables reset for new structure."))
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
            create_command = "create table unicode_chars(" \
                            "uchar_id INT not null auto_increment primary key, " \
                            "uchar VARCHAR(10) not null, " \
                            "char_name VARCHAR(60) not null " \
                            ")"
            self.cursor.execute(create_command)
            #TODO: what to put in the unicode chars table
        self.cursor.execute("SHOW TABLES LIKE 'shape_edits'")
        if self.cursor.fetchone() is None:
            create_command = "create table shape_edits(" \
                            "id INT not null auto_increment primary key, " \
                            "shape_id INT not null, " \
                            "prev_parent INT not null, " \
                            "new_parent INT not null, " \
                            "user INT not null, " \
                            "date DATETIME " \
                            ")"
            self.cursor.execute(create_command)
        self.cursor.execute("SHOW TABLES LIKE 'labeller_users'")
        if self.cursor.fetchone() is None:
            create_command = "create table labeller_users(" \
                            "id INT not null auto_increment primary key, " \
                            "user VARCHAR(60) not null" \
                            ")"
            self.cursor.execute(create_command)
        self.cursor.execute("SHOW TABLES LIKE 'fonts'")
        if self.cursor.fetchone() is None:
            create_command = "create table fonts(" \
                            "id INT not null auto_increment primary key, " \
                            "font VARCHAR(60) not null" \
                            ")"
            self.cursor.execute(create_command)
        self.cursor.execute("SHOW TABLES LIKE 'font_sizes'")
        if self.cursor.fetchone() is None:
            create_command = "create table font_sizes(" \
                            "id INT not null auto_increment primary key, " \
                            "font_size VARCHAR(60) not null" \
                            ")"
            self.cursor.execute(create_command)

    def shape_edit(self, shape_id, prev_parent_id, new_parent_id):
        query = "UPDATE shapes SET parent_id = " + str(new_parent_id) + " WHERE id = " + str(shape_id)
        self.cursor.execute(query)
        query = "INSERT INTO shape_edits(user, shape_id, prev_parent, new_parent, date) VALUES('" \
                + str(self.db_user)+"', " + str(shape_id) + ", " + str(prev_parent_id) + ", " + str(new_parent_id) + ", now())"
        self.cursor.execute(query)

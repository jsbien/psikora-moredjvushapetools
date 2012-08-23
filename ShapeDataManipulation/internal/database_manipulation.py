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

import MySQLdb as mdb
from datatypes import *


class DatabaseManipulator:
    
    def __init__(self, db_name, db_host, db_user, db_pass):
        self.db_name = db_name
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.connection = mdb.connect(db_host, db_user, db_pass, db_name, use_unicode = True)
        self.connection.set_character_set('utf8')
        with self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute('SET NAMES utf8;')
            self.cursor.execute('SET CHARACTER SET utf8;')
            self.cursor.execute('SET character_set_connection=utf8;') 
            self.prepare_database_for_labelling()
    
    def commit(self):
        self.connection.commit()
    
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
    
    def fetch_character_data(self):
        self.cursor.execute("SELECT * FROM unicode_chars")
        data = self.cursor.fetchall()
        unicode_chars = {}
        uchars_by_id = {}
        for db_id, uchar, uchar_name in data:
            unicode_char = UnicodeChar(db_id, uchar, uchar_name)
            unicode_chars[uchar] = unicode_char
            uchars_by_id[db_id] = unicode_char
        return unicode_chars, uchars_by_id
    
    def fetch_labels_raw_data(self, document_id):

        self.cursor.execute("SELECT * FROM labels WHERE document_id = %s", (document_id))
        data = self.cursor.fetchall()
        return data
    
    def fetch(self, fields, table):
        query = "SELECT `" + "`, `".join(fields) + "` FROM " + table
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data
        
    def fetch_junction_table(self, table, selection = "*"):
        self.cursor.execute("SELECT " + selection + "  FROM " + table)
        data = self.cursor.fetchall()
        junction_dictionary = {}
        for id_1, id_2 in data:
            if id_1 in junction_dictionary:
                junction_dictionary[id_1].append(id_2)
            else:
                junction_dictionary[id_1] = [id_2]
        return junction_dictionary
    
    def fetch_simple(self, table):
        self.cursor.execute("SELECT * from " + str(table))
        data = self.cursor.fetchall()
        processed_data = {}
        for db_id, field in data:
            processed_data[db_id] = field
        return processed_data
    
    def insert_simple(self, table, field, value):
        self.cursor.execute("INSERT INTO `" + table + "`(`" + field +"`) VALUES (%s)", value.encode("utf-8"))
        return self.cursor.lastrowid

    def insert_into_junction(self, table, fields, values):
        placeholders = ['%s'] * len(fields)
        self.cursor.execute("INSERT INTO `" + table + "`(`" + "`, `".join(fields) + "`) VALUES(" + ', '.join(placeholders) + ")", values)
    
    def update_junction(self, table, updated_field, other_field, new_value, previous_value, other_value):
        query = "UPDATE " + table + " SET " + updated_field + " = %s WHERE " + updated_field + " = %s AND " + other_field + " = %s"
        self.cursor.execute(query, (new_value, previous_value, other_value))
    
    def insert_label(self, label, user_id, document_id):
        values = (label.font_id, label.font_size_id, label.font_type_id, label.textel_type, document_id, user_id, label.noise)
        self.cursor.execute("INSERT INTO `labels`(`font`, `font_size`, `font_type`, `textel_type`, `document_id`, `user`, `date`, `noise`) VALUES(%s, %s, %s, %s, %s, %s, now(), %s)", values)
        return self.cursor.lastrowid

    def update_label(self, label, user_id, document_id):
        values = (label.font_id, label.font_size_id, label.font_type_id, label.textel_type, document_id, user_id, label.noise, label.db_id)
        query = "UPDATE labels SET " \
                "font = %s, font_size = %s, font_type = %s, textel_type = %s, " \
                "document_id = %s, user = %s, date = now(), noise = %s " \
                "WHERE id = %s"
        self.cursor.execute(query, values)
        
    def insert_uchar(self, character, character_name):
        self.cursor.execute("INSERT INTO `unicode_chars`(`uchar`, `char_name`) VALUES(%s, %s)", (character, character_name))
        return self.cursor.lastrowid
    
    """
    Update labels.
    def update_shape_noise(self, label_id, noise):
        query = "UPDATE shapes SET noise = %s WHERE id = %s"
        self.cursor.execute(query, (shape_id, noise))
    """
    
    def shape_edit(self, shape_id, prev_parent_id, new_parent_id, user_id):
        query = "UPDATE shapes SET parent_id = " + str(new_parent_id) + " WHERE id = " + str(shape_id)
        self.cursor.execute(query)
        query = "INSERT INTO shape_edits(user, shape_id, prev_parent, new_parent, date) VALUES('" \
                + str(user_id)+"', " + str(shape_id) + ", " + str(prev_parent_id) + ", " + str(new_parent_id) + ", now())"
        self.cursor.execute(query)
    
    def reset_database_for_labelling(self):
        self.cursor.execute("DROP TABLE IF EXISTS labels")
        self.cursor.execute("DROP TABLE IF EXISTS shape_edits")
        self.cursor.execute("DROP TABLE IF EXISTS labelled_shapes")
        self.cursor.execute("DROP TABLE IF EXISTS label_chars")
    
    def _prepare_simple_table(self, table, field):
        self.cursor.execute("SHOW TABLES LIKE '" + table + "'")
        if self.cursor.fetchone() is None:
            create_command = "create table " + table + \
                            "(id INT not null auto_increment primary key, " \
                            + field + " VARCHAR(60) not null" \
                            ")"
            self.cursor.execute(create_command)
    
    def _prepare_table_key(self, table, field, properties = "INT not null"):
        command = "SHOW COLUMNS FROM " + table + " LIKE '" + field + "'"
        self.cursor.execute(command)
        if self.cursor.fetchone() is None:
            command = "ALTER TABLE " + table +" ADD " + field + " " + properties + ";"
            self.cursor.execute(command)
    
    def _alter_table_field(self, table, field, properties):
        command = "ALTER TABLE " + table + " MODIFY " + field + ' ' + properties
        self.cursor.execute(command)
    
    def prepare_database_for_labelling(self):
        self.cursor.execute("SHOW TABLES LIKE 'labels'")
        if self.cursor.fetchone() is None:
            create_command = "create table labels(" \
                            "id INT not null auto_increment primary key, " \
                            "font INT not null, " \
                            "font_size INT not null, " \
                            "font_type INT not null, " \
                            "textel_type ENUM('mikrotekstel', 'tekstel właściwy', 'makrotekstel') not null, " \
                            "document_id INT not null, " \
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

            #self._prepare_table_key("labels", "font_typeface")
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
        self._prepare_simple_table("labeller_users", "username")
        self._prepare_simple_table("fonts", "font")
        self._prepare_simple_table("font_sizes", "font_size")
        self._prepare_simple_table("font_types", "font_type")
        self._prepare_table_key("labels", "font_type")        
        self._prepare_table_key("labels", "noise", 
                                "BOOLEAN COMMENT 'If true this shape is not text, but a smear or other graphical noise.'")
        self._prepare_table_key("label_chars", "sequence", "INT not null COMMENT 'Denotes the sequence of characters in a label.'")
        self._alter_table_field('labels', 'font', 'INT null')
        self._alter_table_field('labels', 'font_size', 'INT null')
        self._alter_table_field('labels', 'font_type', 'INT null')
        self._alter_table_field('labels', 'textel_type', "ENUM('mikrotekstel', 'tekstel właściwy', 'makrotekstel') null")

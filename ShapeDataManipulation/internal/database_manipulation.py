'''
@author: Piotr Sikora
'''

import MySQLdb as mdb
from datatypes import *


class DatabaseManipulator:
    
    def __init__(self, db_name, db_host, db_user, db_pass):
        self.db_name = db_name
        self.db_host = db_host
        self.db_user = db_user
        self.db_pass = db_pass
        self.connection = mdb.connect(db_host, db_user, db_pass, db_name)
        with self.connection:
            self.cursor = self.connection.cursor()
    
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
        
    
    def fetch_shapes(self, dictionary_id):
        """ Fetches shapes from a single dictionary
        """
        self.cursor.execute("SELECT * FROM shapes WHERE dictionary_id = "+str(dictionary_id))
        data = self.cursor.fetchall()
        shapes = []
        for shape_data in data:
            shapes.append(Shape(shape_data))
        return shapes
    
    """
    Unpacking shapes:
    
    Unpacking dictionaries:
    for dict_id, dict_name, page_number, document_id in data:
    Unpacking documents:
    doc_id, docname = row
    Unpacking blits:
    for blit_id, document_id, page_number, shape_id, b_left, b_bottom
    """
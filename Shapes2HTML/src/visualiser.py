#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Mar 9, 2012

@author: Piotr Sikora
'''

import MySQLdb as mdb
import Image
import os
import sys
import argparse
import codecs

page_folder = "_files"

page_types = ["database", "document", "dictionary", "shape"]

extension = {"shape":".png"}

def path_to_file(index, page_type, subdir = None):
    assert page_type in page_types
    retval = page_folder + os.sep 
    if subdir:
        retval += subdir + os.sep
    retval += page_type + '_' + str(index) + extension.get(page_type, ".xhtml")
    return retval 

def make_page(page_title, page_type, data):
    xhtml_page = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

    <html xmlns="http://www.w3.org/1999/xhtml">

    <head>
    <title>'''
    xhtml_page += page_title;
    xhtml_page += '''
    </title>
    </head>

    <body>
    '''
    
    #input the body of the page
    assert page_type in page_types
    if page_type == "database":
        for row in data:
            doc_id, docname = row
            xhtml_page += "<a href=\"" + path_to_file(doc_id, "document")+"\">" + docname + "</a><br/>"
    elif page_type == "document":
        xhtml_page += "<table border=\"1\">"
        xhtml_page += "<th>Dictionary</th>"
        xhtml_page += "<th>from page no.:</th>"
        for dict_id, dict_name, page_number, _ in data:
            xhtml_page += "<tr>"
            xhtml_page += "<td>"
            xhtml_page += "<a href=\".." + os.sep + path_to_file(dict_id, "dictionary")+"\">" + dict_name + "</a><br/>"
            xhtml_page += "</td>"
            xhtml_page += "<td>"
            if page_number < 0:
                xhtml_page += "inherited"
            else:
                xhtml_page += "p. " + str(page_number)
            xhtml_page += "</td>"
            xhtml_page += "</tr>"
            
            
        xhtml_page += "</table>" 
    elif page_type == "dictionary":
        xhtml_page += "<table border=\"1\" cellpadding=\"10\">"
        xhtml_page += "<th>Shape #</th>"
        xhtml_page += "<th>Id in document</th>"
        xhtml_page += "<th>Image</th>"
        xhtml_page += "<th>Parent #</th>"
        xhtml_page += "<th>Bounding box left</th>"
        xhtml_page += "<th>Bounding box bottom</th>"
        xhtml_page += "<th>Bounding box top</th>"
        xhtml_page += "<th>Bounding box right</th>"
        
        
        for sh_id, original_id, parent_id, _, width, height, dict_id, bbox_top, bbox_left, bbox_right, bbox_bottom in data:
            xhtml_page += "<tr>"
            xhtml_page += "<td>" + str(sh_id) + "</td>"
            xhtml_page += "<td>" + str(original_id) + "</td>"
            xhtml_page += "<td>" + "<img src=\".." + os.sep + path_to_file(sh_id,"shape", subdir = "dictionary_" + str(dict_id)) + "\" width=\"" + str(width) + "\" height=\"" + str(height) + "\" />" + "</td>"
            if parent_id < 0:
                parent = "no parent"
            else:
                parent = str(parent_id)
            xhtml_page += "<td>" + parent + "</td>"
            xhtml_page += "<td>" + str(bbox_left) + "</td>" + "<td>" + str(bbox_bottom) + "</td>" + "<td>" + str(bbox_top) + "</td>" + "<td>" + str(bbox_right) + "</td>"  
            xhtml_page += "</tr>\n"
        xhtml_page += "</table>" 
        
    
    #finish the page
    xhtml_page += '''
    </body>
    
    </html>'''
    return xhtml_page


def special_print(bits):
    to_process = bits
    while len(to_process) > 0:
        string = ""
        for k in range(10):
            string += str(ord(to_process[k])) + " "
        print string    
        to_process = to_process[10:]

def behead(pbm, width, height):
    ''' 
    GUTF8String head;
    head.format("P%c\n%d %d\n", (raw ? '4' : '1'), ncolumns, nrows);
    bs.writall((void*)(const char *)head, head.length());
    '''
    #
    bytes_to_eliminate = 5 + len(str(width)) + len(str(height))
    return pbm[bytes_to_eliminate:]

def save_image_file(shape_row):
    #id, parent_id, bits, width, height, dictionary_id, bbox_top, bbox_left, bbox_right, bbox_bottom"
    index, _, _, bits, width, height, dict_id, _, _, _, _ = shape_row 
    imagebits = behead(bits, width, height)
    size = width, height
    image = Image.fromstring("1", size, imagebits, "raw", "1;I", 0, 1)
    image.save(path_to_file(index, "shape", subdir = "dictionary_"+str(dict_id)),"png");
     
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a xhtml page presenting the contents of a DjVu shape database.', conflict_handler='resolve')
    parser.add_argument("-h","--host", required=True, dest="db_host")
    parser.add_argument("-d","--database", required=True, dest="db_name")
    parser.add_argument("-u","--user", required=True, dest="db_user")
    parser.add_argument("-p","--password", required=True, dest="db_pass")
    args = parser.parse_args()    
    db_name = args.db_name 
    db_user = args.db_user
    db_pass = args.db_pass
    db_host = args.db_host
    con = None
    try:
        con = mdb.connect(db_host, db_user, db_pass, db_name);
        #global page_folder
        page_folder = db_name + page_folder
        if not os.path.exists(page_folder):
            os.mkdir(page_folder)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM documents")
            document_data = cur.fetchall()
            
            xhtml = make_page(db_name, "database", document_data)
            
            #make a file
            filename = db_name + "_index.xhtml"
            f = open(filename, 'w')
            f.write(xhtml)
            
            #create dictionary pages
            for doc_id, docname in document_data:
                cur.execute("SELECT * FROM dictionaries WHERE document_id = "+str(doc_id))
                dict_data = cur.fetchall()
                xhtml = make_page(docname, "document", dict_data)
                filename = path_to_file(doc_id, "document")
                f = open(filename, 'w')
                f.write(xhtml)
               
                for dict_id, dict_name, _, _ in dict_data:
                    cur.execute("SELECT * FROM shapes WHERE dictionary_id = "+str(dict_id))
                    shape_data = cur.fetchall()
                    xhtml = make_page(docname, "dictionary", shape_data)
                    filename = path_to_file(dict_id, "dictionary")
                    f = open(filename, 'w')
                    f.write(xhtml)
                    dictionary_folder = page_folder+os.sep+"dictionary_" + str(dict_id)
                    if not os.path.exists(dictionary_folder):  
                        os.mkdir(dictionary_folder)
                    for shape_row in shape_data:
                        save_image_file(shape_row)

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:    
        if con:    
            con.close()

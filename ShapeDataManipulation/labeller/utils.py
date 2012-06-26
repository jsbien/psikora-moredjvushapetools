'''
@author: Piotr Sikora
'''

from ocrodjvu import hocr
from ocrodjvu.errors import MalformedHocr
import sys
from os import sep

def page_of_hocr_data(filename, document_name):
    
    doc = document_name.split(sep)[-1].replace('.djvu','')
    if filename[len(doc):len(doc)+5] == '-page' and filename[len(filename)-5:] == '.html':
        page_no = int(filename.replace('.html','')[len(doc)+5:])
        with open(filename) as stream:
            try:
                hocr_page_data = hocr.extract_text(stream, details = hocr.TEXT_DETAILS_CHARACTER)[0]
                return (page_no, hocr_page_data)
            except MalformedHocr as malformed_hocr_exception:
                print("File: "+ str(filename) + " caused exception: " + str(malformed_hocr_exception))
                return (page_no, None)
    return None

    

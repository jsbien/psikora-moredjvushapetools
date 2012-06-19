'''
@author: Piotr Sikora
'''

from lxml import etree

def page_of_hocr_data(filename, document_name):
    doc = document_name.replace('.djvu','')
    if filename[len(doc):len(doc)+5] == '-page' and filename[len(filename)-5:] == '.html':
        page_no = int(filename.replace('.html','')[len(doc)+5:])
        hocr_page_data = hOCR_Page(filename) 
        return (page_no, hocr_page_data)
    return None

class hOCR_Page:
    
    def __init__(self, filename):
        hocr_tree = etree.parse(filename)
    

# -*- coding: utf-8 -*-
'''
    hOCR Labeller of DjVu shapes    
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
from ocrodjvu import hocr
from ocrodjvu.errors import MalformedHocr
import sys
from os import sep
import unicodedata


def page_of_hocr_data(path, filename, document_name):
    doc = document_name.split(sep)[-1].replace('.djvu','')
    if filename[len(doc):len(doc)+5] == '-page' and filename[len(filename)-5:] == '.html':
        page_no = int(filename.replace('.html','')[len(doc)+5:])
        with open(path + sep + filename) as stream:
            try:
                hocr_page_data = hocr.extract_text(stream, details = hocr.TEXT_DETAILS_CHARACTER)[0]
                return (page_no, hocr_page_data)
            except MalformedHocr as malformed_hocr_exception:
                print("File: "+ str(filename) + " caused exception: " + str(malformed_hocr_exception))
                return (page_no, None)
    return None

def unicode_codestr(characters):
    codestrs = []
    for char in characters:
        codestrs.append(str(ord(char)))
    return ', '.join(codestrs)
        
def unicode_names(characters):
    names = []
    for char in characters:
        names.append(unicodedata.name(unicode(char)))
    return ', '.join(names)

    
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.x_end = x + width
        self.y_end = y + height
    
    def center(self):
        center_x = (self.x + self.x_end) / 2
        center_y = (self.y + self.y_end) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x <= other.x_end and self.x_end >= other.x and
                self.y <= other.y_end and self.y_end >= other.y)

    def __str__(self):
        return "Rectangle at " + str(self.x) + ", " + str(self.y) + " w, h: " + str(self.w) + ", " + str(self.h)

from datetime import datetime
debug = open("debug.txt","a+")
debug.write("Execution started " +repr(datetime.now()) + "\n")

def log(message):
    debug.write(message + "\n")
    
def save_hocr(stream):
    pass
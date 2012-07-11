# encoding=UTF-8
# djvu2hocr modified for DjVu hOCR Labeller needs by Piotr Sikora
# Copyright © 2009, 2010, 2011 Jakub Wilk <jwilk@jwilk.net>
# Copyright © 2012 Piotr Sikora <piotr.sikora@student.uw.edu.pl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import re

from . import hocr
from . import text_zones

from .version import __version__

from .hocr import etree
from .text_zones import const
#from .text_zones import sexpr

_xml_string_re = re.compile(
    u'''
    ([^\x00-\x08\x0b\x0c\x0e-\x1f]*)
    ( [\x00-\x08\x0b\x0c\x0e-\x1f]?)
    ''',
    re.UNICODE | re.VERBOSE
)

def set_text(element, text):
    last = None
    for match in _xml_string_re.finditer(text):
        if match.group(1):
            if last is None:
                element.text = match.group(1)
            else:
                last.tail = match.group(1)
        if match.group(2):
            last = etree.Element('span')
            last.set('class', 'djvu_char')
            last.set('title', '#x%02x' % ord(match.group(2)))
            last.text = ' '
            element.append(last)


hocr_header = '''\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="ocr-system" content="%(ocr_system)s" />
  <meta name="ocr-capabilities" content="%(ocr_capabilities)s" />
  <title>hOCR</title>
</head>
<body>
'''
hocr_footer = '''
</body>
</html>
'''

def process_node(parent, node, last, page_h):
    zone_type = node.type
    if zone_type <= const.TEXT_ZONE_LINE and parent is not None:
        parent.tail = '\n'
    try:
        hocr_tag, hocr_class = hocr.djvu_zone_to_hocr(zone_type)
    except LookupError:
        raise
    element = etree.Element(hocr_tag)
    element.set('class', hocr_class)
    bbox = make_bbox(node, page_h)
    n_children = len(node)
    if zone_type == text_zones.const.TEXT_ZONE_WORD:
        bboxes = []
        text = node.text
        for char_node in iter(node):
            bboxes.append(make_bbox(char_node, page_h))
        element.set('title', 'bbox %(bbox)s; bboxes %(bboxes)s' % dict(
            bbox=' '.join(map(str, bbox)),
            bboxes=', '.join(' '.join(map(str, bbox)) for bbox in bboxes)
        ))
        set_text(element, text)
        if element is not None and not last:
            element.tail = ' '
    else:
        element.set('title', 'bbox ' + ' '.join(map(str, bbox)))
        for n, child_node in enumerate(iter(node)):
            last_child = n == n_children - 1
            process_node(element, child_node, last=last_child, page_h = page_h)
    if parent is not None:
        parent.append(element)
    return element

def make_bbox(node, page_h):
    return text_zones.BBox(node.x, page_h - node.y - node.h, node.x + node.w, page_h - node.y)

def save_hocr(stream, data):
    stream.write(
        hocr_header % dict(
            ocr_system='djvu2hocr %s' % __version__,
            ocr_capabilities=' '.join(hocr.djvu2hocr_capabilities)
    ))
    result = process_node(None, data.root, last = True, page_h = data.root.h)
    tree = etree.ElementTree(result)
    tree.write(stream, encoding='UTF-8')
    stream.write(hocr_footer)

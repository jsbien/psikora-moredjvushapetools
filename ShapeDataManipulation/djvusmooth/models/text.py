# encoding=UTF-8
# Copyright © 2008, 2009 Jakub Wilk <jwilk@jwilk.net>
#
# Modified for MoreDjVuShapeTools by Piotr Sikora
# Copyright © 2012 Piotr Sikora <piotr.sikora@student.uw.edu.pl>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

'''
Models for hOCR text.

See Lizardtech DjVu Reference (DjVu 3):
- 3.3.2 Hidden text.
- 8.3.5 Text Chunk.

hOCR documentation
https://docs.google.com/document/preview?id=1QQnIQtvdAC_8n92-LhwPcjtAUFwBlzE8EWnKAxlgVf0
'''

import copy
import weakref
import itertools

import djvu.decode
import djvu.sexpr

from djvusmooth.varietes import not_overridden, wref
from djvusmooth.models import MultiPageModel

class Node(object):

    def __new__(cls, sexpr, owner):
        if len(sexpr) == 6 and isinstance(sexpr[5], djvu.sexpr.StringExpression):
            cls = LeafNode
        else:
            cls = InnerNode
        return object.__new__(cls)

    def __init__(self, sexpr, owner):
        self._owner = owner
        self._type = djvu.const.get_text_zone_type(sexpr[0].value)
        x0, y0, x1, y1 = (sexpr[i].value for i in xrange(1, 5))
        self._x = x0
        self._y = y0
        self._w = x1 - x0
        self._h = y1 - y0
        self._link_left = self._link_right = self._link_parent = wref(None)
        self.shapes = []
        self.blits = []
        self.shape_selected = False
        
    @property
    def sexpr(self):
        return self._construct_sexpr()

    def _construct_sexpr(self):
        raise NotImplementedError

    @apply
    def separator():
        def get(self):
            return djvu.const.TEXT_ZONE_SEPARATORS[self._type]
        return property(get)

    @apply
    def x():
        def get(self):
            return self._x
        def set(self, value):
            self._x = value
            self._notify_change()
        return property(get, set)

    @apply
    def y():
        def get(self):
            return self._y
        def set(self, value):
            self._y = value
            self._notify_change()
        return property(get, set)

    @apply
    def w():
        def get(self):
            return self._w
        def set(self, value):
            self._w = value
            self._notify_change()
        return property(get, set)

    @apply
    def h():
        def get(self):
            return self._h
        def set(self, value):
            self._h = value
            self._notify_change()
        return property(get, set)


    def _get_rect(self):
        return self._x, self._y, self._w, self._h
    def _set_rect(self, value):
        self._x, self._y, self._w, self._h = value
        self._notify_change()
    rect = property(_get_rect, _set_rect) 

    @apply
    def type():
        def get(self):
            return self._type
        return property(get)

    @apply
    def left_sibling():
        def get(self):
            link = self._link_left()
            if link is None:
                raise StopIteration
            return link
        return property(get)

    @apply
    def right_sibling():
        def get(self):
            link = self._link_right()
            if link is None:
                raise StopIteration
            return link
        return property(get)

    @apply
    def parent():
        def get(self):
            link = self._link_parent()
            if link is None:
                raise StopIteration
            return link
        return property(get)

    @apply
    def left_child():
        def get(self):
            raise StopIteration
        return property(get)

    def delete(self):
        try:
            parent = self.parent
        except StopIteration:
            return
        parent.remove_child(self)

    def remove_child(self, child):
        raise NotImplementedError

    def strip(self, zone_type):
        raise NotImplementedError

    def is_leaf(self):
        return False

    def is_inner(self):
        return False

    def notify_select(self):
        self._owner.notify_node_select(self)

    def notify_deselect(self):
        self._owner.notify_node_deselect(self)

    def _notify_change(self):
        return self._owner.notify_node_change(self)

    def _notify_children_change(self):
        return self._owner.notify_node_children_change(self)

    def get_leafs(self):
        return _get_leafs(self)

    def get_preorder_nodes(self):
        return _get_preorder_nodes(self)

    def get_postorder_nodes(self):
        return _get_postorder_nodes(self)

class LeafNode(Node):

    def is_leaf(self):
        return True

    def __init__(self, sexpr, owner):
        Node.__init__(self, sexpr, owner)
        self._text = sexpr[5].value.decode('UTF-8', 'replace')
        

    def _construct_sexpr(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        return djvu.sexpr.Expression((self.type, x, y, x + w, y + h, self.text))

    @apply
    def text():
        def get(self):
            return self._text
        def set(self, value):
            self._text = value
            self._notify_change()
        return property(get, set)

    def remove_child(self, child):
        raise TypeError('%r is not having children' % (self,))

    def strip(self, zone_type):
        if self.type <= zone_type:
            return self.text, self.separator
        return self

    def __getitem__(self, n):
        raise TypeError

    def __len__(self):
        raise TypeError

    def __iter__(self):
        raise TypeError

    

class InnerNode(Node):

    def is_inner(self):
        return True

    def __init__(self, sexpr, owner):
        Node.__init__(self, sexpr, owner)
        self._set_children(Node(child, self._owner) for child in sexpr[5:])

    def _set_children(self, children):
        self._children = list(children)
        prev = None
        for child in self._children:
            child._link_left = wref(prev)
            child._link_parent = wref(self)
            prev = child
        prev = None
        for child in reversed(self._children):
            child._link_right = wref(prev)
            prev = child

    def _construct_sexpr(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        if self._children:
            child_sexprs = (child.sexpr for child in self)
        else:
            # FIXME: this needs a better solution
            child_sexprs = (djvu.sexpr.Expression(''),)
        return djvu.sexpr.Expression(
            itertools.chain(
                (self.type, x, y, x + w, y + h),
                child_sexprs
            )
        )

    @apply
    def text():
        def get(self):
            text = ''
            for child in self._children:
                text += child.text
            return text
        return property(get)

    @apply
    def left_child():
        def get(self):
            return iter(self._children).next()
        return property(get)

    def remove_child(self, child):
        child_idx = self._children.index(child)
        if child_idx - 1 >= 0:
            self._children[child_idx - 1]._link_right = child._link_right
        if child_idx + 1 < len(self._children):
            self._children[child_idx + 1]._link_left = child._link_left
        child._link_left = child._link_right = child._link_parent = wref(None)
        del self._children[child_idx]
        self._notify_children_change()

    def strip(self, zone_type):
        stripped_children = [child.strip(zone_type) for child in self._children]
        if self.type <= zone_type:
            texts = [text for text, child_separator in stripped_children]
            return child_separator.join(texts), self.separator
        else:
            node_children = [child for child in stripped_children if isinstance(child, Node)]
            if node_children:
                self._set_children(node_children)
                return self
            else:
                texts = [text for text, child_separator in stripped_children]
                text = child_separator.join(texts)
                return Node(
                    djvu.sexpr.Expression((
                        self.type,
                        self.x, self.y,
                        self.x + self.w, self.y + self.h,
                        text
                    )), self._owner
                )
        return self

    def __getitem__(self, n):
        return self._children[n]

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return iter(self._children)

class Text(MultiPageModel):

    def get_page_model_class(self, n):
        return PageText

class PageTextCallback(object):

    @not_overridden
    def notify_node_change(self, node):
        pass

    @not_overridden
    def notify_node_children_change(self, node):
        pass

    @not_overridden
    def notify_node_select(self, node):
        pass

    @not_overridden
    def notify_node_deselect(self, node):
        pass

    @not_overridden
    def notify_tree_change(self, node):
        pass

class PageText(object):

    def __init__(self, n, original_data):
        self._callbacks = weakref.WeakKeyDictionary()
        self._original_sexpr = original_data
        self.revert()
        self._n = n
        self._current_line = 0
        self._current_word = 0
        self._current_char = 0
        self._lines = None
        self._words = None
        self._chars = None
        self._current_zone = djvu.const.TEXT_ZONE_LINE
        self._current_node = 0
        
    def _get_current_line_node(self):
        return self.lines[self.current_line]
    current_line_node = property(_get_current_line_node)

    def _get_current_char_node(self):
        return self._get_current_line_chars()[self.current_char]
    current_char_node = property(_get_current_char_node)

    def _extract_zone_nodes(self, zone):
        return [
                 node
                 for node in self.get_preorder_nodes()
                 if node is not None and node.type == zone
                ]

    def _get_lines(self):
        if self._lines is None:
            self._lines = self._extract_zone_nodes(djvu.const.TEXT_ZONE_LINE)
        return self._lines
    lines = property(_get_lines)

    def _get_words(self):
        if self._words is None:
            self._words = self._extract_zone_nodes(djvu.const.TEXT_ZONE_WORD)
        return self._words
    words = property(_get_words)

    def _get_current_line_chars(self):
        return [
                 node
                 for node in self.current_line_node.get_leafs()
                 if node is not None and node.type == djvu.const.TEXT_ZONE_CHARACTER
                ]
    
    def _get_chars(self):
        if self._chars is None:
            self._chars = self._extract_zone_nodes(djvu.const.TEXT_ZONE_CHARACTER)
        return self._chars
    chars = property(_get_chars)
    
    def get_current_char(self):
        return self._current_char
    def set_current_char(self, value):
        self._current_char = value
        self.notify_tree_change()
    current_char = property(get_current_char, set_current_char)
    
    def get_current_line(self):
        return self._current_line
    def set_current_line(self, value):
        self._current_line = value
    current_line = property(get_current_line, set_current_line)

    def register_callback(self, callback):
        if not isinstance(callback, PageTextCallback):
            raise TypeError
        self._callbacks[callback] = 1

    @apply
    def root():
        def get(self):
            return self._root
        return property(get)

    @apply
    def raw_value():
        def get(self):
            if self._root is None:
                return None
            return self._root.sexpr
        def set(self, sexpr):
            if sexpr:
                self._root = Node(sexpr, self)
            else:
                self._root = None
            self.notify_tree_change()
        return property(get, set)

    def strip(self, zone_type):
        zone_type = djvu.const.get_text_zone_type(zone_type) # ensure it's not a plain Symbol
        if self._root is None:
            return
        stripped_root = self._root.strip(zone_type)
        if not isinstance(stripped_root, Node):
            stripped_root = None
        self._root = stripped_root
        self.notify_tree_change()

    def clone(self):
        return copy.copy(self)

    def export(self, djvused):
        if not self._dirty:
            return
        djvused.select(self._n + 1)
        djvused.set_text(self.raw_value)

    def revert(self):
        self.raw_value = self._original_sexpr
        self._dirty = False

    def notify_node_change(self, node):
        self._dirty = True
        for callback in self._callbacks:
            callback.notify_node_change(node)

    def notify_node_children_change(self, node):
        self._dirty = True
        for callback in self._callbacks:
            callback.notify_node_children_change(node)

    def notify_node_select(self, node):
        for callback in self._callbacks: callback.notify_node_select(node)

    def notify_node_deselect(self, node):
        for callback in self._callbacks: callback.notify_node_deselect(node)

    def notify_tree_change(self):
        self._dirty = True
        for callback in self._callbacks:
            callback.notify_tree_change(self._root)
            
    def get_preorder_nodes(self):
        if self.root is None:
            return ()
        return _get_preorder_nodes(self.root)

    def get_postorder_nodes(self):
        if self.root is None:
            return ()
        return _get_postorder_nodes(self.root)

    def get_leafs(self):
        if self.root is None:
            return ()
        return _get_leafs(self.root)

def _get_preorder_nodes(node):
    yield node
    if isinstance(node, LeafNode):
        return
    for child in node:
        for item in _get_preorder_nodes(child):
            yield item

def _get_postorder_nodes(node):
    if isinstance(node, InnerNode):
        for child in node:
            for item in _get_postorder_nodes(child):
                yield item
    yield node

def _get_leafs(node):
    if isinstance(node, LeafNode):
        yield node
    else:
        for child in node:
            for item in _get_leafs(child):
                yield item

__all__ = 'Text', 'PageText'


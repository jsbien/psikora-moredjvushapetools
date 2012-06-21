# encoding=UTF-8

# Copyright © 2008, 2009, 2010, 2011, 2012 Jakub Wilk <jwilk@jwilk.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import functools
import locale
import os
import re
import warnings

debian = os.path.exists('/etc/debian_version')

def enhance_import_error(exception, package, debian_package, homepage):
    message = str(exception)
    format = '%(message)s; please install the %(package)s package'
    if debian:
        package = debian_package
    else:
        format += ' <%(homepage)s>'
    exception.args = [format % locals()]

def parse_page_numbers(pages):
    '''
    parse_page_numbers(None) -> None
    parse_page_numbers('17') -> [17]
    parse_page_numbers('37-42') -> [37, 38, ..., 42]
    parse_page_numbers('17,37-42') -> [17, 37, 38, ..., 42]
    parse_page_numbers('42-37') -> []
    parse_page_numbers('17-17') -> [17]
    '''
    if pages is None:
        return
    result = []
    for page_range in pages.split(','):
        if '-' in page_range:
            x, y = map(int, page_range.split('-', 1))
            result += xrange(x, y + 1)
        else:
            result += int(page_range, 10),
    return result

_special_chars_replace = re.compile(ur'''[\x00-\x1f'"\x5c\x7f-\x9f]''', re.UNICODE).sub

def _special_chars_escape(m):
    ch = m.group(0)
    if ch in ('"', "'"):
        return '\\' + ch
    else:
        return repr(ch)[2:-1]

def smart_repr(s, encoding=None):
    if encoding is None:
        return repr(s)
    try:
        u = s.decode(encoding)
    except UnicodeDecodeError:
        return repr(s)
    return "'%s'" % _special_chars_replace(_special_chars_escape, u)

class EncodingWarning(UserWarning):
    pass

_control_characters_regex = re.compile('[%s]' % ''.join(
    ch for ch in map(chr, xrange(32))
    if ch not in u'\n\r\t'
))

def sanitize_utf8(text):
    '''
    Replace invalid UTF-8 sequences and control characters (except CR, LF, TAB
    and space) with Unicode replacement characters.
    '''
    try:
        text = text.decode('UTF-8')
    except UnicodeDecodeError, exc:
        text = text.decode('UTF-8', 'replace')
        message = str(exc)
        message = re.sub("^'utf8' codec can't decode ", '', message)
        warnings.warn(
            message,
            category=EncodingWarning,
            stacklevel=2,
        )
    text = text.encode('UTF-8')
    match = _control_characters_regex.search(text)
    if match:
        byte = ord(match.group())
        message = 'byte 0x%02x in position %d: control character' % (byte, match.start())
        warnings.warn(
            message,
            category=EncodingWarning,
            stacklevel=2,
        )
        text = _control_characters_regex.sub(u'\N{REPLACEMENT CHARACTER}'.encode('UTF-8'), text)
    # There are other code points that are not allowed in XML (or even: not
    # allowed in UTF-8), but which Python happily accept. However, they haven't
    # seemed to occur in real-world documents.
    # http://www.w3.org/TR/2008/REC-xml-20081126/#NT-Char
    return text

class NotOverriddenWarning(UserWarning):
    pass

def not_overridden(f):
    '''
    Raise warning (NotOverriddenWarning) if the decorated method was not
    overridden in a subclass, or called directly.
    '''
    @functools.wraps(f)
    def new_f(self, *args, **kwargs):
        cls = type(self)
        warnings.warn(
            '%s.%s.%s() is not overridden' % (cls.__module__, cls.__name__, f.__name__),
            category=NotOverriddenWarning,
            stacklevel=2
        )
        return f(self, *args, **kwargs)
    return new_f

def str_as_unicode(s, encoding=locale.getpreferredencoding()):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding, 'replace')

def identity(x):
    '''
    identity(x) -> x
    '''
    return x

class property(object):

    def __init__(self, default_value=None, filter=identity):
        self._private_name = '__%s__%d' % (self.__module__, id(self))
        self._filter = filter
        self._default_value = default_value

    def __get__(self, instance, cls):
        if instance is None:
            return self
        return getattr(instance, self._private_name, self._default_value)

    def __set__(self, instance, value):
        setattr(instance, self._private_name, self._filter(value))
        return

# vim:ts=4 sw=4 et

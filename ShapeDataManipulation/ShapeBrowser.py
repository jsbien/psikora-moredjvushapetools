#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    DjVu Shape Browser    
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

import wxversion
wxversion.select('2.8-unicode')
import wx

import argparse
from browser.frame import ShapeBrowser

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Opens a GUI browser of the contents of a DjVu shape database.', conflict_handler='resolve')
    parser.add_argument("-h","--host", required=True, dest="db_host")
    parser.add_argument("-d","--database", required=True, dest="db_name")
    parser.add_argument("-u","--user", required=True, dest="db_user")
    parser.add_argument("-p","--password", required=True, dest="db_pass")
    args = parser.parse_args()    
    db_name = args.db_name
    db_user = args.db_user
    db_pass = args.db_pass
    db_host = args.db_host
    
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = ShapeBrowser(parent = None, title = u'Przeglądarko-etykieciarka kształtów DjVu')
    frame.connect_to_database(db_name, db_host, db_user, db_pass)
    frame.load_last_session()
    app.MainLoop()

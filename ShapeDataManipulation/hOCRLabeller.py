#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Piotr Sikora
'''

import wxversion
wxversion.select('2.8-unicode')
import wx
from labeller.frame import hOCRLabeller

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A GUI tool for labelling DjVu shapes contained in a database with the help of hOCR data.', conflict_handler='resolve')
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
    frame = hOCRLabeller(parent = None, title = "Etykieciarka hOCR") # A Frame is a top-level window.
    frame.connect_to_database(db_name, db_host, db_user, db_pass)
    frame.load_last_session()
    app.MainLoop()
    
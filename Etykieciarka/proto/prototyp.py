#!/usr/bin/python
# -*- coding: utf-8 -*-
    
import wxversion
wxversion.select('2.8-unicode')
import wx

class FakeHierarchy:
    def __init__(self):
        self.shapes = []
        self.parent = {}
        self.children = {}
        for i in range(1,8):
            shape_image = wx.Image("shape_"+str(i)+".png", wx.BITMAP_TYPE_ANY)
            self.shapes.append(shape_image)
        self.parent[0] = 0
        self.parent[1] = 1
        self.parent[2] = 1
        self.parent[3] = 2
        self.parent[4] = 2
        self.parent[5] = 3
        self.parent[6] = 6
        self.children[0] = [2,3] 
        self.children[1] = [4,5]
        self.children[2] = [6]
        self.children[3] = []
        self.children[4] = []
        self.children[5] = [7]
        self.children[6] = []

    def __getitem__(self, i):
        print(str(i))
        return self.shapes[i]
    
def choose_hierarchy():
    pass

def get_hierarchies_panel():
    pass

if __name__ == '__main__':
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = wx.Frame(None, wx.ID_ANY, "Prototypiarka") # A Frame is a top-level window.
    frame.Show(True)
    frame.CreateStatusBar()
    menu = wx.Menu()
    menu.Append(wx.ID_ABOUT, "&O programie"," Informacje o programie")
    menu.AppendSeparator()
    menu.Append(wx.ID_EXIT,"&Wyjście"," Wyjście z programu")
    menubar = wx.MenuBar()
    menubar.Append(menu, "&Baza")
    frame.SetMenuBar(menubar)
    mainPanel = wx.Panel(frame)
    
    
    hierarchies = []
    hierarchies.append(FakeHierarchy())
    hierarchies.append(FakeHierarchy())

    mainSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    leftSizer = wx.BoxSizer(wx.VERTICAL)

    # a panel for choosing hierarchies
    hierarchiesPanel = wx.Panel(mainPanel)
    hierarchiesPanel.SetBackgroundColour('#000000')
    hierarchiesSizer = wx.BoxSizer(wx.HORIZONTAL)
    root1 = wx.StaticBitmap(hierarchiesPanel, -1, wx.BitmapFromImage(hierarchies[0][0]))
    root2 = wx.StaticBitmap(hierarchiesPanel, -1, wx.BitmapFromImage(hierarchies[0][2]))
    hierarchiesSizer.Add(root1, 1, wx.ALIGN_CENTER_VERTICAL, 5 )
    hierarchiesSizer.Add(root2, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, 5 )
    
    hierarchiesPanel.SetSizer(hierarchiesSizer)
    # a panel for displaying a hierarchy
    #borderPanel = wx.Panel(mainPanel)
    #borderSizer = wx.BoxSizer(wx.HORIZONTAL)
    shapesPanel = wx.Panel(mainPanel)
    #shapesPanel.SetBackgroundColour('#00ff00')
    shapesSizer = wx.GridSizer(rows=3, cols=3, hgap=5, vgap=5)
    
    shapeBitmaps = []
    for i in range(7):
        shapeBitmaps.append(wx.StaticBitmap(shapesPanel, -1, wx.BitmapFromImage(hierarchies[0][i])))
    shapesSizer.AddMany(shapeBitmaps)
    
    
    
    shapesPanel.SetSizer(shapesSizer)
    
    #borderSizer.Add(shapesSizer, 1, wx.EXPAND, 10)
    #borderPanel.SetSizer(borderSizer)
    
    leftSizer.Add(hierarchiesPanel,1, wx.EXPAND, 5)
    leftSizer.Add(shapesPanel,5, wx.EXPAND, 5)
    
    
    
    # a panel to label a shape
    labelPanel = wx.Panel(mainPanel)
    #labelPanel.SetBackgroundColour('#0000ff')
    labelSizer = wx.BoxSizer(wx.VERTICAL)
    
    currentShape = wx.StaticBitmap(labelPanel, -1, wx.BitmapFromImage(hierarchies[0][1]))
    label1 = wx.StaticText(labelPanel, wx.ID_ANY, "Rozmiar fontu:")
    label2 = wx.StaticText(labelPanel, wx.ID_ANY, "Krój fontu:")
    label3 = wx.StaticText(labelPanel, wx.ID_ANY, "Postać:")
    label4 = wx.StaticText(labelPanel, wx.ID_ANY, "Typ tekstela")
    label5 = wx.StaticText(labelPanel, wx.ID_ANY, "Tekstel:")
    label6 = wx.StaticText(labelPanel, wx.ID_ANY, "nazwa tekstela w unicodzie")
    textCtrl1 = wx.TextCtrl(labelPanel)
    textCtrl2 = wx.TextCtrl(labelPanel)
    textCtrl3 = wx.TextCtrl(labelPanel)
    textCtrl4 = wx.TextCtrl(labelPanel)
    
    checkboxesSizer = wx.BoxSizer(wx.HORIZONTAL)
    cb1 = wx.RadioButton(labelPanel, wx.ID_ANY, "właściwy")
    cb2 = wx.RadioButton(labelPanel, wx.ID_ANY, "makrotekstel")
    cb3 = wx.RadioButton(labelPanel, wx.ID_ANY, "mikrotekstel")
    checkboxesSizer.Add(cb1, 1, wx.ALIGN_CENTER, 1)
    checkboxesSizer.Add(cb2, 1, wx.ALIGN_CENTER, 1)
    checkboxesSizer.Add(cb3, 1, wx.ALIGN_CENTER, 1)
    
    labelSizer.Add(currentShape , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(label1 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(textCtrl1 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(label2 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(textCtrl2 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(label3 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(textCtrl3 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(label4 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(checkboxesSizer, 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(label5 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(textCtrl4 , 1, wx.ALIGN_CENTER, 1)
    labelSizer.Add(label6 , 1, wx.ALIGN_CENTER, 1)
    
    labelPanel.SetSizer(labelSizer)
    
    
    
    
    
    mainSizer.Add(leftSizer,1, wx.EXPAND, 5)
    mainSizer.Add(labelPanel,1, wx.EXPAND, 5)
    
    mainPanel.SetSizer(mainSizer)
    
    
    
    
    
    
    
    app.MainLoop()
    
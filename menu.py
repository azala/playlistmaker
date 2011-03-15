import wx, sys
import wx.gizmos as gz
import plvars as plv
from playlistmaker import *

class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Playlistmaker v0.1', size=(400,400))
        #self.log = log
        self.itemData = {}
        self.CenterOnScreen()
        self.CreateStatusBar()
        menubar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1exit = menu1.Append(wx.ID_EXIT, '&Exit', 'Exit Playlistmaker')
        menubar.Append(menu1, '&File')
        
        self.Bind(wx.EVT_MENU, self.OnExit, menu1exit)
        #context menu
        

        self.SetMenuBar(menubar)
        self.Show(True)

        plTreePanel = wx.Panel(self, wx.ID_ANY, pos=(5,5), size=(190,390))
        plTreePanel.Show(True)
        self.plTree = gz.TreeListCtrl(plTreePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                      wx.TR_DEFAULT_STYLE
                                      | wx.TR_HAS_BUTTONS
                                      | wx.TR_TWIST_BUTTONS
                                      | wx.TR_MULTIPLE
                                      | wx.TR_HIDE_ROOT)
        self.plTree.AddColumn('Files')
        self.plTree.SetColumnWidth(0, 200)
        self.plTree.AddColumn('Rating')
        self.plTree.AddColumn('Tags')
        self.plTree.SetMainColumn(0)
        self.plTree.SetColumnAlignment(1, wx.ALIGN_CENTER)
        
        self.plTree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnMouseRightDown)
        
        self.root = self.plTree.AddRoot('')
        #sample sizer code
        bdr = wx.BoxSizer(wx.HORIZONTAL)
        bdr.Add(self.plTree, 1, wx.EXPAND|wx.ALL, 15)
        plTreePanel.SetSizer(bdr)
        bdr.Fit(plTreePanel)
    def OnExit(self, event):
        self.Close(True)
    def OnMouseRightDown(self, event):
        menu = wx.Menu()
        item = wx.MenuItem(menu, wx.NewId(), 'Rating -> 0')
        menu.Bind(wx.EVT_MENU, self.OnRatingZero, item)
        menu.AppendItem(item)
        self.PopupMenu(menu)
        menu.Destroy()
    def OnRatingZero(self, event):
        for s in self.plTree.GetSelections():
            x = GetChildren(self.plTree, s)
            if len(x) == 0:
                fn = self.plTree.GetItemPyData(s)
                self.itemData[fn].rating = 0
                self.updateItem(s)
    def fillTagTree(self):
        knownFiles = []
        for t in plkeysSorted():
            tagNode = self.plTree.AppendItem(self.root, t)
            for fn in sorted(plv.playlists[t], key=lambda x: plv.fileNames2sortKeys[x]):
                if fn not in knownFiles:
                    knownFiles.append(fn)
                    sd = SongNodeData()
                    sd.fileName = fn
                    sd.sortKey = plv.fileNames2sortKeys[fn]
                    sd.rating = rating(fn)
                    sd.tags = plv.taglists[fn]
                    self.itemData[fn] = sd
                child = self.plTree.AppendItem(tagNode, '')
                self.plTree.SetItemPyData(child, fn)
                self.updateItem(child)
    def updateItem(self, item):
        sd = self.itemData[self.plTree.GetItemPyData(item)]
        self.plTree.SetItemText(item, sd.fileName.rpartition('\\')[2], 0)
        self.plTree.SetItemText(item, ratingToString(sd.rating), 1)
        self.plTree.SetItemText(item, tagListToString(sd.tags), 2)

def GetChildren(tree, item):
    l = []
    x = tree.GetFirstChild(item)[0]
    while x.IsOk():
        print tree.GetItemPyData(x)
        l.append(x)
        x = tree.GetNextSibling(x)
    return l
        
class SongNodeData(object):
    fileName = ''
    sortKey = ''
    rating = 0
    tags = []
        
def main(argv):
    app = wx.App(False)
    frame = MyFrame(None, wx.ID_ANY)
    frame.Show(True)
    frame.fillTagTree()
    app.MainLoop()

if __name__ == "__main__":
    main(sys.argv)
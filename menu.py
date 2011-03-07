import wx, sys
import wx.gizmos as gz
import plvars as plv
from playlistmaker import *

class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Playlistmaker v0.1', size=(400,400))
        #self.log = log
        self.CenterOnScreen()
        self.CreateStatusBar()
        menubar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1exit = menu1.Append(wx.ID_EXIT, '&Exit', 'Exit Playlistmaker')
        menubar.Append(menu1, '&File')
        self.Bind(wx.EVT_MENU, self.OnExit, menu1exit)
        self.SetMenuBar(menubar)
        self.Show(True)

        plTreePanel = wx.Panel(self, wx.ID_ANY, pos=(5,5), size=(190,390))
        plTreePanel.Show(True)
        self.plTree = wx.TreeCtrl(plTreePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                  wx.TR_DEFAULT_STYLE
                                  | wx.TR_MULTIPLE
                                  | wx.TR_HIDE_ROOT)
        self.root = self.plTree.AddRoot('Tags')
        #sample sizer code
        bdr = wx.BoxSizer(wx.HORIZONTAL)
        bdr.Add(self.plTree, 1, wx.EXPAND|wx.ALL, 15)
        plTreePanel.SetSizer(bdr)
        bdr.Fit(plTreePanel)
    def OnExit(self, event):
        self.Close(True)
    def fillTagTree(self):
        for t in plkeysSorted():
            tagNode = self.plTree.AppendItem(self.root, t)
            for fn in sorted(plv.playlists[t], key=lambda x: plv.fileNames2sortKeys[x]):
                self.plTree.AppendItem(tagNode, fn.rpartition('\\')[2])
        
def main(argv):
    app = wx.App(False)
    frame = MyFrame(None, wx.ID_ANY)
    frame.Show(True)
    frame.fillTagTree()
    app.MainLoop()

if __name__ == "__main__":
    main(sys.argv)
import wx, sys

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
        plTree = wx.TreeCtrl(plTreePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE)
        root = plTree.AddRoot('Root')
        child = plTree.AppendItem(root, "Child")

        
    def OnExit(self, event):
        self.Close(True)
        
def main(argv):
    app = wx.App(False)
    frame = MyFrame(None, wx.ID_ANY)
    frame.Show(True)
    app.MainLoop()

if __name__ == "__main__":
    main(sys.argv)

import wx
import os

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.mainFrame = wx.Frame.__init__(self, parent, title = title, size=(300, -1))

        #text editor
        self.control = wx.TextCtrl(self, style = wx.TE_MULTILINE)

        #set-up menu
        fileMenu = wx.Menu()
        m_about = fileMenu.Append(wx.ID_ANY, 'about', 'info about this program')
        fileMenu.AppendSeparator()
        m_exit = fileMenu.Append(wx.ID_ANY, 'exit', 'exit!')
        fileMenu.AppendSeparator()
        m_open = fileMenu.Append(wx.ID_ANY, 'open', 'open file')

        #creating menubar (on top of frame)
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, 'File')
        self.SetMenuBar(menuBar)

        #binding events
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        self.Bind(wx.EVT_MENU, self.OnExit, m_exit)
        self.Bind(wx.EVT_MENU, self.OnOpen, m_open)

        self.btnSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttons = []
        for i in range(0, 3):
            self.buttons.append(wx.Button(self, -1, 'Button #{}'.format(i)))
            self.btnSizer.Add(self.buttons[i], 1, wx.EXPAND)
        
        self.quote = wx.StaticText(self, label = 'dupa', style = )
        self.btnSizer.Add(self.quote, 1, wx.EXPAND)

        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.control, 1, wx.EXPAND)
        self.mainSizer.Add(self.btnSizer, 0, wx.EXPAND)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.mainSizer.Fit(self)
        self.Show(True)

    def OnAbout(self, event):
        aboutDialog = wx.MessageDialog(self, 'small text editor', 'about sample editor')
        aboutDialog.ShowModal()
        aboutDialog.Destroy()
        
    def OnExit(self, event):
        self.Close(True)

    def OnOpen(self, event):
        self.dirname = ''
        fileDialog = wx.FileDialog(self, "Pick a file", self.dirname, '', '*.*', wx.FD_OPEN)
        if fileDialog.ShowModal() == wx.ID_OK:
            self.filename = fileDialog.GetFilename()
            self.dirname = fileDialog.GetDirectory()
            file = open(os.path.join(self.dirname, self.filename), 'r')
            self.control.SetValue(file.read())
            file.close()
        fileDialog.Destroy()

if __name__ == '__main__':
    app = wx.App(False)
    MainFrame(None, 'dupa')
    app.MainLoop()
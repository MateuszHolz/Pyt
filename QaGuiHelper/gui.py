import wx
import os

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.mainFrame = wx.Frame.__init__(self, parent, title = title, size=(300, -1))

        #text editor
        self.console = Console(self)

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

        #creating test sizeers and their content
        self.btnSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttons = []
        for i in range(0, 3):
            self.buttons.append(wx.Button(self, -1, 'Button #{}'.format(i)))
            self.btnSizer.Add(self.buttons[i], 1, wx.EXPAND)

        newBtn = wx.Button(self, -1, 'addtoconsole')
        self.btnSizer.Add(newBtn, 1, wx.EXPAND)

        self.txtField = wx.TextCtrl(self)
        self.btnSizer.Add(self.txtField, 1, wx.EXPAND)
        
        self.quote = wx.StaticText(self, label = 'dupa', style = wx.ALIGN_CENTRE_HORIZONTAL)
        self.btnSizer.Add(self.quote, 1, wx.EXPAND)

        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.btnSizer, 1, wx.EXPAND)
        self.mainSizer.Add(self.console, 0, wx.EXPAND)

        #binding events
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        self.Bind(wx.EVT_MENU, self.OnExit, m_exit)
        self.Bind(wx.EVT_MENU, self.OnOpen, m_open)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.buttons[0])
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.buttons[1])
        self.Bind(wx.EVT_BUTTON, self.AddToConsole, newBtn)
        self.Bind(wx.EVT_TEXT, self.OnChangeTxtFieldText, self.txtField)
        self.Bind(wx.EVT_CHAR, self.OnChangeTxtFieldChar, self.txtField)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.mainSizer.Fit(self)
        self.Show(True)
    
    def OnClear(self, event):
        self.console.clear()

    def OnChangeTxtFieldChar(self, event):
        print('OnChangeTxtFieldChar')
    
    def OnChangeTxtFieldText(self, event):
        print('OnChangeTxtFieldText')

    def AddToConsole(self, event):
        self.console.addText('dupa123\n')

    def OnAbout(self, event):
        aboutDialog = wx.MessageDialog(self, 'small text editor', 'about sample editor')
        aboutDialog.ShowModal()
        aboutDialog.Destroy()
        
    def OnExit(self, event):
        self.Close(True)

    def OnButton(self, event):
        print('d')

    def OnButton2(self, event):
        msgBox = wx.MessageDialog(self, 'dialog content', 'dialog header')
        msgBox.ShowModal()
        msgBox.Destroy()

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

class Console(wx.TextCtrl):
    def __init__(self, parent):
        self.console = wx.TextCtrl.__init__(self, parent, style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.curLines = 0

    def clear(self):
        self.SetValue('')

    def addText(self, text):
        if self.curLines >= 5:
            print('yes')
            self.Remove(0, self.GetLineLength(0))
        else:
            print('no')
        self.AppendText(text)
        self.curLines += 1

if __name__ == '__main__':
    app = wx.App(False)
    MainFrame(None, 'dupa')
    app.MainLoop()
import os
import threading
import time

import wx


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.mainFrame = wx.Frame.__init__(self, parent, title = title, size=(-1, -1))
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        #creating devices panel and placing it on first place in box sizer
        self.devicesPanel = DevicesPanel(self)
        self.mainSizer.Add(self.devicesPanel, 1)
        #creating Console object and place it on second place in box sizer
        self.console = Console(self)
        self.mainSizer.Add(self.console, 1)

        #set-up top menu
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
        self.Bind(wx.EVT_MENU, self.ShowBusyWindow2, m_exit)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.mainSizer.Fit(self)
        self.Show(True)
        
    def OnExit(self, event):
        self.Close(True)

    def ShowBusyWindow2(self, event):
        disabler = wx.WindowDisabler()
        c = InProgressFrame(self, disabler, self.console)
        c.show()

class Console(wx.TextCtrl):
    def __init__(self, parent):
        self.console = wx.TextCtrl.__init__(self, parent, style = wx.TE_MULTILINE | wx.TE_READONLY, size = (300, 400))
        self.curLines = 0

    def clear(self):
        self.SetValue('')

    def addText(self, text):
        self.AppendText(text+'\n')

class InProgressFrame(wx.Frame):
    def __init__(self, parent, disabler, console):
        self.frame = wx.Frame.__init__(self, parent, title = 'inprogressframe')
        self.disabler = disabler
        self.parent = parent

        self.labelSizer = wx.BoxSizer(wx.VERTICAL)
        self.labels = []
        for i in range(0, 5):
            self.labels.append(wx.TextCtrl(self, style = wx.ALIGN_CENTRE_HORIZONTAL | wx.TE_READONLY))
            self.labelSizer.Add(self.labels[i], 1, wx.EXPAND)
        self.newBtn1 = wx.Button(self, -1, 'ddddd')
        self.labelSizer.Add(self.newBtn1, 1, wx.EXPAND)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.newBtn1)
        self.stopWorking = False
    
    def show(self):
        self.SetSizer(self.labelSizer)
        self.SetAutoLayout(1)
        self.labelSizer.Fit(self)
        self.Show(True)

    def OnButton(self, event):
        self.t = threading.Thread(target = self.worker, args = (self, ))
        self.t.start()
    
    def worker(self, frame):
        for i in range(0, 1000):
            if frame.stopWorking:
                print('stop working')
                return
            self.labels[1].SetValue(str(i))
            time.sleep(0.01)

    def OnClose(self, event):
        self.stopWorking = True
        self.Destroy()
        self.parent.Raise() ## without that, parent frame hides behind opened windows (for example google chrome)

class DevicesPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent, size = (5, 400))
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.checkBoxesPanel = DevicesCheckboxesPanel(self)
        self.refreshButtonPanel = RefreshButtonPanel(self, self.checkBoxesPanel)
        self.sizer.Add(self.refreshButtonPanel, 1, wx.EXPAND, border = 2)
        self.sizer.Add(self.checkBoxesPanel, 10, wx.EXPAND, border = 2)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

class DevicesCheckboxesPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.checkBoxes = []
        for i in self.getListOfDevices():
            checkBx = wx.CheckBox(self, -1, label = i, size = (50, 50), style = wx.ALIGN_RIGHT)
            self.sizer.Add(checkBx, 0, wx.ALIGN_CENTER)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
    
    def getListOfDevices(self):
        return ('asd1', 'asd2', 'asd3')

class RefreshButtonPanel(wx.Panel):
    def __init__(self, parent, devicesPanel):
        self.panel = wx.Panel.__init__(self, parent)
        self.devicesPanel = devicesPanel
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn = wx.Button(self, wx.ID_ANY, 'refresh')
        self.sizer.Add(self.btn, 0, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.refreshDevicesPanel, self.btn)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

    def refreshDevicesPanel(self):
        pass
        
if __name__ == '__main__':
    app = wx.App(False)
    MainFrame(None, 'dupa')
    app.MainLoop()

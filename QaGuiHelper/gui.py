import os
import threading
import time

import wx


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.mainFrame = wx.Frame.__init__(self, parent, title = title, size=(-1, -1))
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.console = Console(self)
        self.devicesPanel = DevicesPanel(self, self.console)

        self.mainSizer.Add(self.devicesPanel, 1)
        self.mainSizer.Add(self.console, 1)

        #set-up top menu
        fileMenu = wx.Menu()
        fileMenu.AppendSeparator()
        m_exit = fileMenu.Append(wx.ID_ANY, 'exit', 'exit!')

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
    def __init__(self, parent, console):
        self.panel = wx.Panel.__init__(self, parent, size = (5, 400))
        self.parent = parent
        self.console = console
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent)
        self.buttonsPanel = RefreshButtonPanel(self)

        self.sizer.Add(self.buttonsPanel, 1, wx.EXPAND)
        self.sizer.Add(self.checkBoxesPanel, 10, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.Fit()
    
    def refreshCheckboxesPanel(self):
        self.sizer.Remove(1)
        self.checkBoxesPanel.Destroy()
        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent)
        self.sizer.Add(self.checkBoxesPanel, 10, wx.EXPAND)
        self.sizer.Layout()
        self.Fit()
        self.parent.Layout()
        self.parent.Fit()
    
    def printCheckedRecords(self):
        checkedRecords = []
        for i, j in zip(self.checkBoxesPanel.checkBoxesCtrls, self.checkBoxesPanel.activeDeviceList):
            if i.GetValue() == True:
                checkedRecords.append(j)
        for i in checkedRecords:
            self.console.addText(i.rstrip())      

class DevicesCheckboxesPanel(wx.Panel):
    def __init__(self, parent, mainWindow):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.mainWindow = mainWindow
        self.activeDeviceList = []
        self.checkBoxesCtrls = []
        self.createPanel()

    def getListOfDevices(self):
        with open('devices.txt', 'r') as f:
            dev = f.readlines()
        return dev

    def createPanel(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.activeDeviceList = self.getListOfDevices()
        id = 0
        for i in self.activeDeviceList:
            # local sizer of one record
            recordSizer = wx.BoxSizer(wx.HORIZONTAL)

            # creating checkbox, adding it to self.checkboxes list (so we can later on get its state), and placing it on local sizer
            checkBx = wx.CheckBox(self, -1, label = i, size = (150, 20), style = wx.ALIGN_RIGHT)
            self.checkBoxesCtrls.append(checkBx)
            recordSizer.Add(checkBx, 0, wx.ALIGN_CENTER)

            # creating info button, binding its EVT_BUTTON event to function that takes its id as parametr and adding the button to local sizer
            infoButton = wx.Button(self, label = 'i', size = (20, 20))
            self.Bind(wx.EVT_BUTTON, self.OnInfoButton(id), infoButton)
            recordSizer.Add(infoButton, 0, wx.ALIGN_CENTER)

            # adding local sizer to main sizer, increasing ID by 1
            mainSizer.Add(recordSizer, 0, wx.ALIGN_CENTER)
            id += 1
        self.SetSizer(mainSizer)
        mainSizer.Layout()
        self.Fit()
    
    def OnInfoButton(self, id):
        def OnClick(event):
            # for debug purposes:
            self.parent.console.addText('id elementu: {} nazwa devica: {}'.format(id, self.activeDeviceList[id]))
            disabler = wx.WindowDisabler()
            DeviceInfoWindow(self, self.mainWindow, id, disabler)
            # TODO: open new window (block its parent from getting input), 
            # show some info about device (by invoking few adb commands). 
            # in future: get info via http get request from Szmegers API
        return OnClick

class RefreshButtonPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.createPanel()

    def createPanel(self):
        topRow = wx.BoxSizer(wx.HORIZONTAL)
        captureSSBtn = wx.Button(self, wx.ID_ANY, 'Capture SS')
        installBuildBtn = wx.Button(self, wx.ID_ANY, 'Install Build')
        topRow.Add(captureSSBtn, 0, wx.ALIGN_CENTER)
        topRow.Add(installBuildBtn, 0, wx.ALIGN_CENTER)

        bottomRow = wx.BoxSizer(wx.HORIZONTAL)
        refreshDevicesBtn = wx.Button(self, wx.ID_ANY, 'Refresh')
        bottomRow.Add(refreshDevicesBtn, 0, wx.ALIGN_CENTER)
        placeholderBtn = wx.Button(self, wx.ID_ANY, 'Placeholder')
        bottomRow.Add(placeholderBtn, 0, wx.ALIGN_CENTER)

        self.sizer.Add(topRow, 0, wx.ALIGN_CENTER)
        self.sizer.Add(bottomRow, 0, wx.ALIGN_CENTER)

        self.Bind(wx.EVT_BUTTON, self.getStateOfCheckboxes, captureSSBtn)
        self.Bind(wx.EVT_BUTTON, self.getAndInstallBuild, installBuildBtn)
        self.Bind(wx.EVT_BUTTON, self.refreshDevicesPanel, refreshDevicesBtn)
        self.Bind(wx.EVT_BUTTON, self.placeholderMethod, placeholderBtn)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

    def refreshDevicesPanel(self, event):
        self.parent.refreshCheckboxesPanel()

    def getStateOfCheckboxes(self, event):
        self.parent.printCheckedRecords()
    
    def getAndInstallBuild(self, event):
        print('getAndInstallBuild')

    def placeholderMethod(self, event):
        print('placeholderMethod')

class DeviceInfoWindow(wx.Frame):
    def __init__(self, parent, mainWindow, deviceId, disabler):
        self.window = wx.Frame.__init__(self, parent, title = 'Device Info')
        self.parent = parent
        self.mainWindow = mainWindow
        self.deviceId = deviceId
        self.disabler = disabler
        self.info = self.getDeviceInfo()
        self.createControls()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Show(True)

    def getDeviceInfo(self, mock = False):
        # TO DO - change this function to return proper info of device (using its unique id)
        localList = []
        res = '1920x1080'
        localList.append(('Device Resolution', res))
        aspectRatio = '16:9'
        localList.append(('Aspect Ratio', aspectRatio))
        ip = '192.168.0.255'
        localList.append(('IP Address', ip))
        batteryStatus = '95%'
        localList.append(('Battery', batteryStatus))
        return localList
    
    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        for i in self.info:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label = i[0], size = (100, -1))
            sizer.Add(label, 0, wx.EXPAND)
            content = wx.TextCtrl(self, value = i[1], style = wx.TE_READONLY)
            sizer.Add(content, 0, wx.ALIGN_RIGHT)
            mainSizer.Add(sizer, 0)
        self.SetSizer(mainSizer)
        self.SetAutoLayout(1)
        mainSizer.Fit(self)

    def OnClose(self, event):
        self.Destroy()
        self.mainWindow.Raise() ## without that, parent frame hides behind opened windows (for example google chrome)
    

if __name__ == '__main__':
    app = wx.App(False)
    MainFrame(None, 'ADB GUI')
    app.MainLoop()

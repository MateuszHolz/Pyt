import os ##to do: implement method to check if directory exists in optionsHandler class
import wx

from Adb import Adb
from BuildInstallerFrame import BuildInstallerFrame
from DeviceInfoFrame import DeviceInfoFrame
from JenkinsMenu import JenkinsMenu
from OptionsHandler import OptionsHandler
from OptionsFrame import OptionsFrame
from ScreenshotCaptureFrame import ScreenshotCaptureFrame

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title = title, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.optionsHandler = OptionsHandler()
        self.adb = Adb()

        menuBar, optionsMenuButton, exitMenuButton = self.createMenuBar()

        self.mainPanel = wx.Panel(self)

        captureSSBtn, installBtn, refreshBtn, self.mainSizer, self.bottomSizer = self.createControls()

        self.Bind(wx.EVT_BUTTON, self.updateBottomSizer, refreshBtn)
        self.Bind(wx.EVT_BUTTON, self.openScreenshotPanel, captureSSBtn)
        self.Bind(wx.EVT_BUTTON, self.openInstallBuildPanel, installBtn)
        self.Bind(wx.EVT_CLOSE, self.onExit)
        self.Bind(wx.EVT_MENU, self.showOptions, optionsMenuButton)
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuButton)

        self.SetMenuBar(menuBar)
        self.scaleTheWindow()
        self.Show(True)

    def scaleTheWindow(self):
        self.mainPanel.Layout()
        self.mainSizer.Layout()
        self.mainPanel.Fit()
        self.Fit()

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        topSizer, captureSSBtn, installBtn, refreshBtn = self.createButtonSizer()
        mainSizer.Add(topSizer, 0, wx.EXPAND | wx.ALL, 5)
        bottomSizer = self.createListOfDevicesSizer()
        mainSizer.Add(bottomSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.mainPanel.SetSizer(mainSizer)
        self.mainPanel.Fit()

        return captureSSBtn, installBtn, refreshBtn, mainSizer, bottomSizer

    def createButtonSizer(self):
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        captureSSButton = wx.Button(self.mainPanel, wx.ID_ANY, 'Capture SS')
        buttonsSizer.Add(captureSSButton, 1, wx.EXPAND | wx.ALL, 5)
        installBuildsButton = wx.Button(self.mainPanel, wx.ID_ANY, 'Install Build')
        buttonsSizer.Add(installBuildsButton, 1, wx.EXPAND | wx.ALL, 5)
        refreshDevicesButton = wx.Button(self.mainPanel, wx.ID_ANY, 'Refresh')
        buttonsSizer.Add(refreshDevicesButton, 1, wx.EXPAND | wx.ALL, 5)

        return buttonsSizer, captureSSButton, installBuildsButton, refreshDevicesButton

    def createListOfDevicesSizer(self):
        deviceList = self.adb.getListOfAttachedDevices()

        listOfDevicesSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftColumn = wx.BoxSizer(wx.VERTICAL)
        middleColumn = wx.BoxSizer(wx.VERTICAL)
        rightColumn = wx.BoxSizer(wx.VERTICAL)
        columnNameFont = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)

        leftColumnLabel = wx.StaticText(self.mainPanel, label = 'Device', style = wx.CENTER)
        leftColumnLabel.SetFont(columnNameFont)
        leftColumn.Add(leftColumnLabel, 1, wx.CENTER | wx.ALL, 3)

        middleColumnLabel = wx.StaticText(self.mainPanel, label = 'State', style = wx.CENTER)
        middleColumnLabel.SetFont(columnNameFont)
        middleColumn.Add(middleColumnLabel, 1, wx.CENTER | wx.ALL, 3)

        rightColumnLabel = wx.StaticText(self.mainPanel, label = 'Info', style = wx.CENTER)
        rightColumnLabel.SetFont(columnNameFont)
        rightColumn.Add(rightColumnLabel, 1, wx.CENTER | wx.ALL, 3)

        for i, j in deviceList:
            model = self.adb.getDeviceModel(i)    

            leftColumn.Add(wx.StaticLine(self.mainPanel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            middleColumn.Add(wx.StaticLine(self.mainPanel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            rightColumn.Add(wx.StaticLine(self.mainPanel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)

            modelLabel = wx.StaticText(self.mainPanel, label = model, style = wx.CENTER)
            stateLabel = wx.StaticText(self.mainPanel, label = j, style = wx.CENTER)
            infoButton = wx.Button(self.mainPanel, label = 'i', style = wx.CENTER, size = (20, 5))
            infoButton.info = i, j

            leftColumn.Add(modelLabel, 1, wx.CENTER | wx.ALL, 9)
            middleColumn.Add(stateLabel, 1, wx.CENTER | wx.ALL, 9)
            rightColumn.Add(infoButton, 1, wx.CENTER | wx.ALL, 3)

            self.Bind(wx.EVT_BUTTON, self.showInfoAboutDevice, infoButton)

        listOfDevicesSizer.Add(leftColumn, 1, wx.EXPAND | wx.ALL, 3)
        listOfDevicesSizer.Add(wx.StaticLine(self.mainPanel, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND)
        listOfDevicesSizer.Add(middleColumn, 1, wx.EXPAND | wx.ALL, 3)
        listOfDevicesSizer.Add(wx.StaticLine(self.mainPanel, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND)
        listOfDevicesSizer.Add(rightColumn, 1, wx.EXPAND | wx.ALL, 3)

        return listOfDevicesSizer

    def createMenuBar(self):
        fileMenu = wx.Menu()
        optionsMenuButton = fileMenu.Append(wx.ID_ANY, 'Options')
        fileMenu.AppendSeparator()
        exitMenuButton = fileMenu.Append(wx.ID_ANY, 'Exit')

        jenkinsMenu = JenkinsMenu(self, 'links.json', self.optionsHandler)
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, 'File')
        menuBar.Append(jenkinsMenu, 'Jenkins')

        return menuBar, optionsMenuButton, exitMenuButton

    ### EVENTS ###

    def openScreenshotPanel(self, event):
        if not os.path.exists(self.optionsHandler.getOption('Screenshots folder', str)):
            errorDlg = wx.MessageDialog(self, "Save screenshots directory doesn't exist! Set it in Options -> Screenshots Folder", 'Error!',
                                        style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        ScreenshotCaptureFrame(self, self.adb, self.optionsHandler)

    def openInstallBuildPanel(self, event):
        if not os.path.exists(self.optionsHandler.getOption('Builds folder', str)):
            errorDlg = wx.MessageDialog(self, "Builds directory doesn't exist! Set it in Options -> Builds Folder", 'Error!',
                                        style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        BuildInstallerFrame(self, self.adb, self.optionsHandler)
    
    def updateBottomSizer(self, event):
        newBottomSizer = self.createListOfDevicesSizer()
        self.mainSizer.Hide(self.bottomSizer)
        self.mainSizer.Layout()
        self.mainSizer.Replace(self.bottomSizer, newBottomSizer)
        self.bottomSizer = newBottomSizer
        self.scaleTheWindow()
        self.Fit()

    def onExit(self, event):
        self.optionsHandler.saveOptionsToFile()
        self.Destroy()

    def showOptions(self, event):
        optionsframe.OptionsFrame(self, self.optionsHandler)

    def showInfoAboutDevice(self, event):
        deviceId, state = event.GetEventObject().info
        if state == 'unauthorized':
            errorDlg = wx.MessageDialog(self, "Unauthorized device! Check authorization dialog on device.", 'Unauthorized device!',
                                        style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        DeviceInfoFrame(self, deviceId, self.adb)

if __name__ == '__main__':
    app = wx.App(False)
    MainFrame(None, 'ADB GUI')
    app.MainLoop()

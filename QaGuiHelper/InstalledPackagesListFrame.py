import threading
import wx

class InstalledPackagesListFrame(wx.Frame):
    def __init__(self, parentFrame, deviceId, adb, listOfPackages):
        wx.Frame.__init__(self, parentFrame, title = 'Installed packages', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.parentFrame = parentFrame
        self.deviceId = deviceId
        self.adb = adb
        self.listOfPackages = listOfPackages
        self.versionInfoDict = {
            'Version Name': self.adb.getBuildVersionNameFromDevice,
            'Version Code': self.adb.getBuildVersionCodeFromDevice,
            'Debug?': self.adb.isInstalledPackageDebuggable
        }

        self.disabler = wx.WindowDisabler(self)
        self.panel = wx.Panel(self)

        self.infoCtrlsUpdateList, self.closeBtn = self.createControls()
        self.runUpdateThreads()
        
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onClose, self.closeBtn)
        self.Fit()
        self.Show(True)

    def createControls(self):
        infoCtrlsUpdateList = []
        '''
        infoCtrlsUpdateList is a list of tuples
        each tuple contains:
        [0] - text ctrl to be updated
        [1] - package name of app
        [2] - function to call
        '''
        labelSize = (200, -1)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        ### First row - header ###
        headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        placeholderLabel = wx.StaticText(self.panel, label = 'Package', size = labelSize, style = wx.TE_CENTRE)
        headerSizer.Add(placeholderLabel, 0, wx.CENTRE | wx.ALL, 3)
        for headerLabel in self.versionInfoDict.keys():
            label = wx.StaticText(self.panel, label = headerLabel, size = labelSize, style = wx.TE_CENTRE)
            headerSizer.Add(label, 0, wx.CENTRE | wx.ALL, 3)
        mainSizer.Add(headerSizer, 0, wx.EXPAND | wx.ALL, 5)

        ### Creating list of packages and info controls ###
        for i in self.listOfPackages:
            rowSizer = wx.BoxSizer(wx.HORIZONTAL)
            packageCtrl = wx.TextCtrl(self.panel, value = i, size = labelSize, style = wx.TE_READONLY)
            rowSizer.Add(packageCtrl, 0, wx.CENTRE | wx.ALL, 3)
            versionNameCtrl = wx.TextCtrl(self.panel, value = '...', size = labelSize, style = wx.TE_READONLY)
            infoCtrlsUpdateList.append((versionNameCtrl, i, self.versionInfoDict['Version Name']))
            rowSizer.Add(versionNameCtrl, 0, wx.CENTRE | wx.ALL, 3)
            versionCodeCtrl = wx.TextCtrl(self.panel, value = '...', size = labelSize, style = wx.TE_READONLY)
            infoCtrlsUpdateList.append((versionCodeCtrl, i, self.versionInfoDict['Version Code']))
            rowSizer.Add(versionCodeCtrl, 0, wx.CENTRE | wx.ALL, 3)
            debugInfoCtrl = wx.TextCtrl(self.panel, value = '...', size = labelSize, style = wx.TE_READONLY)
            infoCtrlsUpdateList.append((debugInfoCtrl, i, self.versionInfoDict['Debug?']))
            rowSizer.Add(debugInfoCtrl, 0, wx.CENTRE | wx.ALL, 3)

            mainSizer.Add(rowSizer, 0, wx.EXPAND | wx.ALL, 5)

        closeBtn = wx.Button(self.panel, wx.ID_ANY, 'Close')
        mainSizer.Add(closeBtn, 0, wx.CENTRE | wx.ALL, 5)


        self.panel.SetSizer(mainSizer)
        self.panel.Fit()
        
        return infoCtrlsUpdateList, closeBtn

    def runUpdateThreads(self):
        for textCtrl, packageName, functionToCall in self.infoCtrlsUpdateList:
            threading.Thread(target = self.updateField, args = (functionToCall, packageName, textCtrl)).start()

    def updateField(self, functionToCall, packageName, textCtrl):
        textCtrl.SetValue(functionToCall(self.deviceId, packageName))

    ### EVENTS ###

    def onClose(self, event):
        del self.disabler
        self.parentFrame.Raise()
        self.Destroy()
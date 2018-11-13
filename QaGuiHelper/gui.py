import json
import os
import re
import requests
import threading
import time
import subprocess
import wx

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.mainFrame = wx.Frame.__init__(self, parent, title = title, size=(-1, -1))
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        optionsPath = os.path.join(os.getenv('APPDATA'), 'adbgui')
        self.optionsFilePath = os.path.join(optionsPath, 'options.json')
        self.__optionsCategories = (
            ('Screenshots folder', 'folder'),
            ('Builds folder', 'folder'),
            ('Jenkins credentials', 'input')
        )
        self.__options = self.getOptionsIfAlreadyExist(optionsPath, self.optionsFilePath)

        self.adb = Adb()
        self.devicesPanel = DevicesPanel(self, self.adb)

        mainSizer.Add(self.devicesPanel, 1)

        fileMenu = wx.Menu()
        options = fileMenu.Append(wx.ID_ANY, 'Options')
        fileMenu.AppendSeparator()
        ext = fileMenu.Append(wx.ID_ANY, 'Exit')

        jenkinsMenu = JenkinsMenu(self, 'links.json')
            
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, 'File')
        menuBar.Append(jenkinsMenu, 'Jenkins')
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.showOptions, options)
        self.Bind(wx.EVT_MENU, self.onExit, ext)
        self.Bind(wx.EVT_CLOSE, self.onExit)

        self.SetSizer(mainSizer)
        self.SetAutoLayout(1)
        mainSizer.Fit(self)
        self.Show(True)

    def getOptionsIfAlreadyExist(self, folderPath, filePath):
        if os.path.exists(folderPath):
            try:
                with open (filePath, 'r') as f:
                    try:
                        return json.loads(f.read())
                    except json.decoder.JSONDecodeError:
                        return {}
            except FileNotFoundError:
                return {}
        else:
            os.mkdir(folderPath)
            return {}
        
    def onExit(self, event):
        self.saveOptionsToFile()
        self.Destroy()

    def showOptions(self, event):
        disabler2 = wx.WindowDisabler()
        OptionsFrame(self, disabler2)

    def setOption(self, option, value):
        self.__options[option] = value

    def getOption(self, option, t = False):
        try:
            return self.__options[option]
        except KeyError:
            if t:
                return ('', '')
            else:
                return ''

    def saveOptionsToFile(self):
        with open(self.optionsFilePath, 'w+') as f:
            json.dump(self.__options, f)

    def getOptionsCategories(self):
        return self.__optionsCategories

class JenkinsMenu(wx.Menu):
    def __init__(self, parent, pathToJsonFile):
        self.menu = wx.Menu.__init__(self)
        self.parent = parent
        links = {}
        with open(pathToJsonFile, 'r') as f:
            links = json.loads(f.read())
        for platforms in links.keys():
            platformMenu = wx.Menu()
            for projects in links[platforms].keys():
                projectMenu = wx.Menu()
                for environment in links[platforms][projects].keys():
                    environmentMenu = wx.Menu()
                    for buildVersion in links[platforms][projects][environment].keys():
                        buildVersionMenu = wx.Menu()
                        for branchOption in links[platforms][projects][environment][buildVersion].keys():
                            menuItem = buildVersionMenu.Append(wx.ID_ANY, branchOption)
                            self.parent.Bind(wx.EVT_MENU, 
                                            self.getBuild(links[platforms][projects][environment][buildVersion][branchOption]),
                                            menuItem)
                        environmentMenu.Append(wx.ID_ANY, buildVersion, buildVersionMenu)
                    projectMenu.Append(wx.ID_ANY, environment, environmentMenu)
                platformMenu.Append(wx.ID_ANY, projects, projectMenu)
            self.Append(wx.ID_ANY, platforms, platformMenu)

    def getBuild(self, info):
        def getBuildEvent(event):
            if len(self.parent.getOption('Jenkins credentials')) != 2:
                errorDlg = wx.MessageDialog(self.parent, 'Please provide your jenkins credentials (file -> options)', 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
                errorDlg.ShowModal()
                return
            buildInfo = RetrieveLinkDialog(self.parent, info).getLink()
            DownloadBuildDialog(self.parent, buildInfo).downloadBuild()
        return getBuildEvent

class OptionsFrame(wx.Frame):
    def __init__(self, parent, disabler):
        self.frame = wx.Frame.__init__(self, parent, title = 'Options')
        self.parent = parent
        self.disabler = disabler

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        for i, j in self.parent.getOptionsCategories():
            localSizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label = i, style = wx.TE_CENTRE, size = (100, 10))
            localSizer.Add(label, 0, wx.EXPAND)
            if j == 'folder':
                valueCtrl = wx.TextCtrl(self, value = self.parent.getOption(i), size = (200, 20), style = wx.TE_READONLY)
                localSizer.Add(valueCtrl, 0, wx.EXPAND)
                editBtn = wx.Button(self, wx.ID_ANY, 'Edit')
                localSizer.Add(editBtn, 0, wx.EXPAND)
                self.Bind(wx.EVT_BUTTON, self.editFileOption(i, valueCtrl), editBtn)
            elif j == 'input':
                inputUsername = wx.TextCtrl(self, value = self.parent.getOption(i, True)[0], size = (100, 20))
                localSizer.Add(inputUsername, 0, wx.EXPAND)
                inputPassword = wx.TextCtrl(self, value = self.parent.getOption(i, True)[1], size = (100, 20))
                localSizer.Add(inputPassword, 0, wx.EXPAND)
                saveBtn = wx.Button(self, wx.ID_ANY, 'Save')
                localSizer.Add(saveBtn, 0, wx.EXPAND)
                self.Bind(wx.EVT_BUTTON, self.editCredentialsOption(i, inputUsername, inputPassword), saveBtn)
            self.sizer.Add(localSizer, 0, wx.EXPAND)

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.show()

    def onClose(self, event):
        self.Destroy()
        self.parent.Raise()
    
    def editFileOption(self, option, valueControl):
        def editOptionEvent(event):
            with wx.DirDialog(self, 'Choose {} path'.format(option)) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    newOption = dlg.GetPath()
                    self.parent.setOption(option, newOption)
                    valueControl.SetValue(newOption)
        return editOptionEvent
    
    def editCredentialsOption(self, option, username, password):
        def editCredentialsEvent(event):
            self.parent.setOption(option, (username.GetValue(), password.GetValue()))
        return editCredentialsEvent

    def show(self):
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show(True)

class RetrieveLinkDialog(wx.GenericProgressDialog):
    def __init__(self, parent, info):
        self.dlg = wx.GenericProgressDialog.__init__(self, 'Working...', 'Retrieving build information...', style = wx.PD_APP_MODAL)
        self.parent = parent
        self.info = info
        self.auth = self.parent.getOption('Jenkins credentials')

    def getLink(self):
        if self.info[1] == '':
            link = self.getDirectLinkToBuild(self.info[0], self.info[2]), self.auth
        else:
            link = self.getDirectLinkToBuild(self.getLinkToLatestBranch(self.info[0], self.info[1]), self.info[2]), self.auth
        self.Close()
        return link

    def getLinkToLatestBranch(self, jobLink, branchName):
        self.Pulse()
        linkContent = self.requestSiteContent(jobLink)
        curBuildName = self.getBuildName(linkContent, '')
        if branchName in curBuildName:
            return jobLink
        else:
            self.Pulse()
            lastCheckedVersionCode = self.getVersionCode(jobLink)
            newLink = '{}{}'.format(jobLink[:jobLink.find('lastSuccessfulBuild')], int(lastCheckedVersionCode)-1)
            while True:
                self.Pulse()
                newSiteContent = self.requestSiteContent(newLink)
                self.Pulse()
                newBuildName = self.getBuildName(newSiteContent, '')
                if branchName in newBuildName:
                    time.sleep(0.2)
                    return newLink
                else:
                    lastCheckedVersionCode = self.getVersionCode(newLink)
                    newLink = '{}{}/'.format(newLink[:newLink.find(lastCheckedVersionCode)], int(lastCheckedVersionCode)-1)
    
    def getVersionCode(self, link):
        siteContent = self.requestSiteContent(link)
        version = siteContent.text.find('Build #')
        version = siteContent.text[version:version+40].split()
        return version[1][1:]

    def getDirectLinkToBuild(self, jobLink, buildVer):
        linkContent = self.requestSiteContent(jobLink)
        buildName = self.getBuildName(linkContent, buildVer)
        buildSize = self.getBuildSize(linkContent, buildName)
        directLink = '{}{}{}'.format(jobLink, '/artifact/output/', buildName)
        return directLink, buildName, buildSize

    def getBuildName(self, siteContent, buildVer):
        for i in siteContent.text.split():
            if "HuuugeStars" in i and buildVer in i and not 'dSYM.zip' in i:
                id1 = i.find("HuuugeStars")
                if i.find(".apk") > 0:
                    id2 = i.find(".apk")+4
                else:
                    id2 = i.find(".ipa")+4
                return i.rstrip()[id1:id2]
        return ''

    def getBuildSize(self, siteContent, buildName):
        localId = siteContent.text.find(buildName)
        cont = siteContent.text[localId:localId+300].split()
        for i in cont:
            if 'fileSize' in i:
                return i[i.find('>')+1:]

    def requestSiteContent(self, link):
        response = requests.get(link, auth = (self.auth[0], self.auth[1]))
        if response.ok:
            return response
        else:
            errorDlg = wx.MessageDialog(self.parent, 'Incorrect response from jenkins! Error code: {}.'.format(response.status_code), 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            self.Destroy()
            return

class DownloadBuildDialog(wx.GenericProgressDialog):
    def __init__(self, parent, info):
        self.parent = parent
        self.info = info
        self.dlg = wx.GenericProgressDialog.__init__(self, 'Downloading build!', self.info[0][1])

    def downloadBuild(self):
        buildFolder = self.parent.getOption('Builds folder')
        response = requests.get(self.info[0][0], auth = (self.info[1][0], self.info[1][1]), stream = True)
        with open(os.path.join(buildFolder, self.info[0][1]), 'wb') as f:
            buildSize = float(self.info[0][2]) * 1048576 
            progress = 0
            updateCount = 0
            for b in response.iter_content(chunk_size = 4096):
                progress += len(b)
                updateCount += 1
                f.write(b)
                curProgress = int((progress / buildSize)* 100)
                if updateCount % 50 == 0:
                    progressInMb = str(float(self.info[0][2]) * (curProgress / 100))
                    self.Update(curProgress, '{} \n {}MB / {}MB'.format(self.info[0][1], progressInMb[:progressInMb.find('.')+3], self.info[0][2]))

class DevicesPanel(wx.Panel):
    def __init__(self, parent, adb):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.adb = adb
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent, self.adb)
        self.buttonsPanel = RefreshButtonPanel(self, self.parent, self.adb)

        self.sizer.Add(self.buttonsPanel, 0, wx.EXPAND | wx.ALL, 15)
        self.sizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
        self.sizer.Add(self.checkBoxesPanel, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(self.sizer)
        self.Fit()
    
    def refreshCheckboxesPanel(self):
        self.sizer.Remove(2)
        self.checkBoxesPanel.Destroy()
        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent, self.adb)
        self.sizer.Add(self.checkBoxesPanel, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)
        self.sizer.Layout()
        self.Fit()
        self.parent.Layout()
        self.parent.Fit()   

class DevicesCheckboxesPanel(wx.Panel):
    def __init__(self, parent, mainWindow, adb):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.adb = adb
        self.mainWindow = mainWindow
        self.activeDeviceList = self.getAuthorizedDevices(self.adb.getListOfAttachedDevices())
        self.checkBoxesCtrls = []
        self.createPanel()

    def getAuthorizedDevices(self, rawList):
        activeList = []
        for i in rawList:
            if i[1] == 'device':
                activeList.append(i[0])
        return activeList

    def createPanel(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftColumn = wx.BoxSizer(wx.VERTICAL)
        middleColumn = wx.BoxSizer(wx.VERTICAL)
        rightColumn = wx.BoxSizer(wx.VERTICAL)
        columnNameFont = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)

        leftColumnLabel = wx.StaticText(self, label = 'Device', style = wx.CENTER)
        leftColumnLabel.SetFont(columnNameFont)
        leftColumn.Add(leftColumnLabel, 1, wx.CENTER | wx.ALL, 3)

        middleColumnLabel = wx.StaticText(self, label = 'Check', style = wx.CENTER)
        middleColumnLabel.SetFont(columnNameFont)
        middleColumn.Add(middleColumnLabel, 1, wx.CENTER | wx.ALL, 3)

        rightColumnLabel = wx.StaticText(self, label = 'Info', style = wx.CENTER)
        rightColumnLabel.SetFont(columnNameFont)
        rightColumn.Add(rightColumnLabel, 1, wx.CENTER | wx.ALL, 3)

        for i in self.activeDeviceList:
            model = self.adb.getDeviceModel(i)    

            leftColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            middleColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            rightColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)

            modelLabel = wx.StaticText(self, label = model, style = wx.CENTER)
            checkBx = wx.CheckBox(self, style = wx.CENTER)
            infoButton = wx.Button(self, label = 'i', style = wx.CENTER)

            leftColumn.Add(modelLabel, 1, wx.CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 3)
            middleColumn.Add(checkBx, 1, wx.CENTER | wx.ALL, 3)
            rightColumn.Add(infoButton, 1, wx.CENTER | wx.ALL, 3)

            self.checkBoxesCtrls.append((checkBx, model))
            self.Bind(wx.EVT_BUTTON, self.OnInfoButton(i), infoButton)

        mainSizer.Add(leftColumn, 1, wx.EXPAND | wx.ALL, 3)
        mainSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND)
        mainSizer.Add(middleColumn, 1, wx.EXPAND | wx.ALL, 3)
        mainSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND)
        mainSizer.Add(rightColumn, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(mainSizer)
        mainSizer.Layout()
        self.Fit()

    def getCheckedDevices(self):
        checkedRecords = []
        for i, j in zip(self.checkBoxesCtrls, self.activeDeviceList):
            if i[0].GetValue() == True:
                checkedRecords.append((j, i[1]))
        return checkedRecords
    
    def OnInfoButton(self, dev):
        def OnClick(event):
            disabler = wx.WindowDisabler()
            DeviceInfoFrame(self, self.mainWindow, dev, disabler, self.adb)
        return OnClick
    
    def switchAllCheckboxes(self, state):
        for i in self.checkBoxesCtrls:
            i[0].SetValue(state)

class RefreshButtonPanel(wx.Panel):
    def __init__(self, parent, mainWindow, adb):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.adb = adb
        self.mainWindow = mainWindow
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.createPanel()
        self.checkAllStatus = True

    def createPanel(self):
        topRow = wx.BoxSizer(wx.HORIZONTAL)
        captureSSBtn = wx.Button(self, wx.ID_ANY, 'Capture SS')
        installBuildBtn = wx.Button(self, wx.ID_ANY, 'Install Build')
        topRow.Add(captureSSBtn, 0, wx.ALIGN_CENTER)
        topRow.Add(installBuildBtn, 0, wx.ALIGN_CENTER)

        bottomRow = wx.BoxSizer(wx.HORIZONTAL)
        refreshDevicesBtn = wx.Button(self, wx.ID_ANY, 'Refresh')
        bottomRow.Add(refreshDevicesBtn, 0, wx.ALIGN_CENTER)
        checkAllButton = wx.Button(self, wx.ID_ANY, 'Select all')
        bottomRow.Add(checkAllButton, 0, wx.ALIGN_CENTER)

        self.sizer.Add(topRow, 0, wx.ALIGN_CENTER)
        self.sizer.Add(bottomRow, 0, wx.ALIGN_CENTER)

        self.Bind(wx.EVT_BUTTON, self.getScreenshotFromDevices, captureSSBtn)
        self.Bind(wx.EVT_BUTTON, self.installBuild, installBuildBtn)
        self.Bind(wx.EVT_BUTTON, self.refreshDevicesPanel, refreshDevicesBtn)
        self.Bind(wx.EVT_BUTTON, self.checkAll(checkAllButton), checkAllButton)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

    def getScreenshotFromDevices(self, event):
        devices = self.parent.checkBoxesPanel.getCheckedDevices()
        if (len(devices)) == 0:
            errorDlg = wx.MessageDialog(self.parent, 'At least 1 device must be selected!', 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        disabler = wx.WindowDisabler()
        ScreenshotCaptureFrame(self, self.mainWindow, disabler, self.adb, devices)

    def refreshDevicesPanel(self, event):
        self.parent.refreshCheckboxesPanel()
    
    def installBuild(self, event):
        devices = self.parent.checkBoxesPanel.getCheckedDevices()
        if (len(devices)) == 0:
            errorDlg = wx.MessageDialog(self.parent, 'At least 1 device must be selected!', 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        disabler = wx.WindowDisabler()
        BuildInstallerFrame(self.mainWindow, disabler, self.adb, devices)

    def checkAll(self, btn):
        def checkAllEvent(event):
            self.parent.checkBoxesPanel.switchAllCheckboxes(self.checkAllStatus)
            self.checkAllStatus = not self.checkAllStatus
            if self.checkAllStatus:
                btn.SetLabel('Select all')
            else:
                btn.SetLabel('Deselect all')
        return checkAllEvent

class DeviceInfoFrame(wx.Frame):
    def __init__(self, parent, mainWindow, deviceId, disabler, adb):
        wx.Frame.__init__(self, parent, title = 'Device Info')
        self.mainWindow = mainWindow
        self.disabler = disabler
        self.panel = DeviceInfoPanel(self, deviceId, adb)
        self.bindEvents()
        self.Fit()

        self.Show(True)
    
    def bindEvents(self):
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        del self.disabler
        self.Destroy()
        self.mainWindow.Raise() ## without that, parent frame hides behind opened windows

    def setSize(self, w, h):
        self.SetSize(w, h)

class DeviceInfoPanel(wx.Panel):
    def __init__(self, parent, deviceId, adb):
        wx.Panel.__init__(self, parent)
        self.deviceId = deviceId
        self.parent = parent
        self.adb = adb
        self.deviceInfoControls = []
        self.deviceInfoTable = (
            ('Brand', self.adb.getBrand),
            ('Model', self.adb.getDeviceModel),
            ('Screen size', self.adb.getDeviceScreenSize),
            ('IP Address', self.adb.getDeviceIpAddress),
            ('ADB tcpip port', self.adb.getTcpipPort),
            ('Battery', self.adb.getBatteryStatus),
            ('Plugged in?', self.adb.getPluggedInStatus),
            ('OS version', self.adb.getOsVersion),
            ('API version', self.adb.getApiVersion),
            ('Device timezone', self.adb.getDeviceTimezone),
            ('Device language', self.adb.getDeviceLanguage),
            ('Marketing name', self.adb.getMarketingName),
            ('Wifi name', self.adb.getWifiName),
            ('Serial No', self.adb.getSerialNo))
        self.createControls()
        self.updateFields()

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        first = True
        for i in self.deviceInfoTable:
            if first:
                first = False
            else:
                mainSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label = i[0], size = (100, -1), style = wx.TE_CENTRE)
            sizer.Add(label, 0, wx.EXPAND | wx.TOP, label.GetSize()[1]/3.5)
            content = wx.TextCtrl(self, value = '...', size = (150, -1), style = wx.TE_READONLY)
            self.deviceInfoControls.append(content)
            sizer.Add(content, 0, wx.ALIGN_RIGHT)
            mainSizer.Add(sizer, 0, wx.ALL, 5)
        self.SetSizer(mainSizer)
        self.SetAutoLayout(1)
        mainSizer.Fit(self)

    def updateFields(self):
        for func, ctrl in zip(self.deviceInfoTable, self.deviceInfoControls):
            localThread = threading.Thread(target = self.updateSingleControl, args = (ctrl, self.deviceId, func[1]))
            localThread.start()

    def updateSingleControl(self, textCtrl, deviceId, functionToCall):
        try:
            textCtrl.SetValue(functionToCall(deviceId))
        except RuntimeError:
            print('got it!')

class ScreenshotCaptureFrame(wx.Frame):
    def __init__(self, parent, mainWindow, disabler, adb, listOfDevices):
        self.frame = wx.Frame.__init__(self, mainWindow, title = 'Capturing screenshots!')
        self.disabler = disabler
        self.mainWindow = mainWindow

        self.panel = ScreenshotCapturePanel(self, adb, listOfDevices, self.mainWindow.getOption('Screenshots folder'))
        self.bindEvents()
        self.Show()

    def bindEvents(self):
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        del self.disabler
        self.Destroy()
        self.mainWindow.Raise()

class ScreenshotCapturePanel(wx.Panel):
    def __init__(self, parent, adb, listOfDevices, directoryForScreenshots):
        self.panel = wx.Panel.__init__(self, parent)
        self.adb = adb
        self.directoryForScreenshots = directoryForScreenshots
        self.listOfDevices = listOfDevices
        self.statusLabels = []
        self.createWindowContent()
        self.deployScreenshotThreads()

    def createWindowContent(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        header = wx.BoxSizer(wx.HORIZONTAL)
        headerLabel = wx.StaticText(self, label = 'Capturing screenshots of {} device(s)'.format(len(self.listOfDevices)), size = (200, 30), style = wx.ALIGN_CENTER)
        header.Add(headerLabel, 0, wx.CENTER)
        mainSizer.Add(header, 0, wx.CENTER)
        for i in self.listOfDevices:
            row = wx.BoxSizer(wx.HORIZONTAL)
            nameLabel = wx.StaticText(self, label = i[1], size = (130, 30), style = wx.ALIGN_RIGHT)
            row.Add(nameLabel, 0, wx.EXPAND | wx.TOP, 10)
            statusLabel = wx.StaticText(self, label = '...', size = (130, 30), style = wx.ALIGN_CENTER)
            row.Add(statusLabel, 0, wx.EXPAND | wx.TOP, 10)
            self.statusLabels.append(statusLabel)
            mainSizer.Add(row, 0)

        self.SetSizer(mainSizer)
        self.SetAutoLayout(1)
        mainSizer.Fit(self)
        self.Show(True)
    
    def deployScreenshotThreads(self):
        if not os.path.exists(self.directoryForScreenshots):
            time.sleep(0.2)
            errorDlg = wx.MessageDialog(self, "Save screenshots directory doesn't exist! Set it in Options -> Screenshots Folder", 'Error!',
                                         style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            self.Close()
            return
        for i, j in zip(self.listOfDevices, self.statusLabels):
            localThread = threading.Thread(target = self.captureAndPullScreenshot, args = (i[0], self.directoryForScreenshots, j, i[1]))
            localThread.start()
        
    def captureAndPullScreenshot(self, device, directory, statusLabel, model):
        statusLabel.SetLabel('Taking screenshot...')
        pathToScreenOnDevice = ''
        fileName = self.getFileName(device, model)
        clbk = self.adb.captureScreenshot(device, fileName)
        try:
            statusLabel.SetLabel(clbk[0])
        except RuntimeError:
            return
        if not clbk[1]:
            return
        pathToScreenOnDevice = clbk[1]
        clbk = self.adb.pullScreenshot(device, pathToScreenOnDevice, directory)
        try:            
            statusLabel.SetLabel(clbk)
        except RuntimeError:
            return
    
    def getFileName(self, device, model):
        unsupportedChars = (' ', '(', ')')
        for i in unsupportedChars:
            model = model.replace(i, '')
        deviceScreenSize = self.adb.getDeviceScreenSize(device)
        return '{}-{}.png'.format(model, deviceScreenSize)

class BuildInstallerFrame(wx.Frame):
    def __init__(self, mainWindow, disabler, adb, deviceList):
        wx.Frame.__init__(self, mainWindow, title = 'Installing builds')
        self.disabler = disabler
        self.mainWindow = mainWindow

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.topPanel = BuildInstallerTopPanel(self, self.mainWindow.getOption('Builds folder'))
        self.bottomPanel = BuildInstallerBottomPanel(self, deviceList, adb)
        self.mainSizer.Add(self.topPanel, 0, wx.EXPAND)
        self.mainSizer.Add(self.bottomPanel, 0, wx.EXPAND)
        self.bindEvents()
        self.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)
        self.Show()
    
    def onClose(self, event):
        del self.disabler
        self.Destroy()
        self.mainWindow.Raise()

    def bindEvents(self):
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def installBuild(self, build):
        self.bottomPanel.installBuild(build)

class BuildInstallerTopPanel(wx.Panel):
    def __init__(self, parent, buildFolder):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.buildFolder = buildFolder
        self.buildChosen = ''
        self.createPanelContent()

    def createPanelContent(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        topRow = wx.BoxSizer(wx.HORIZONTAL)
        selectBuildButton = wx.Button(self, wx.ID_ANY, 'Select build')
        topRow.Add(selectBuildButton, 1, wx.ALL, 5)
        chooseLatestButton = wx.Button(self, wx.ID_ANY, 'Get latest from default folder')
        topRow.Add(chooseLatestButton, 2, wx.ALL, 5)
        mainSizer.Add(topRow, 0, wx.EXPAND)

        bottomRow = wx.TextCtrl(self, value = 'Drag and drop build here', style = wx.TE_READONLY | wx.TE_CENTRE)
        mainSizer.Add(bottomRow, 0, wx.EXPAND | wx.ALL, 5)

        dragAndDropHandler = FileDragAndDropHandler(bottomRow, self)
        bottomRow.SetDropTarget(dragAndDropHandler)

        installButton = wx.Button(self, wx.ID_ANY, 'Install')
        mainSizer.Add(installButton, 0, wx.CENTRE | wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self.startInstallingBuild, installButton)
        self.Bind(wx.EVT_BUTTON, self.getLatestBuildFromOptionsFolder(bottomRow), chooseLatestButton)
        self.Bind(wx.EVT_BUTTON, self.selectBuild(bottomRow), selectBuildButton)
        self.SetSizer(mainSizer)

    def selectBuild(self, textCtrl):
        def selectBuildEvent(event):
            with wx.FileDialog(self, 'Choose build', wildcard = '*.apk', style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:
                if fd.ShowModal() == wx.ID_CANCEL:
                    return ''
                else:
                    self.setBuild(fd.GetPath(), textCtrl)
        return selectBuildEvent

    def getLatestBuildFromOptionsFolder(self, textCtrl):
        def getLatestBuildFromOptionsFolderEvent(event):
            self.setBuild(self.buildFolder, textCtrl)
        return getLatestBuildFromOptionsFolderEvent

    def setBuild(self, build, textCtrl):
        self.buildChosen = build
        textCtrl.SetValue(build)

    def startInstallingBuild(self, event):
        self.parent.installBuild(self.buildChosen)

class BuildInstallerBottomPanel(wx.Panel):
    def __init__(self, parent, deviceList, adb):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.deviceList = deviceList
        self.adb = adb
        self.statusLabels = []
        self.createControls()
        self.Fit()

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftColumn = wx.BoxSizer(wx.VERTICAL)
        rightColumn = wx.BoxSizer(wx.VERTICAL)
        columnNameFont = wx.Font(14, wx.MODERN, wx.ITALIC, wx.LIGHT)

        devColumnNameLabel = wx.StaticText(self, label = 'Device', style = wx.CENTER)
        devColumnNameLabel.SetFont(columnNameFont)
        leftColumn.Add(devColumnNameLabel, 0, wx.CENTER | wx.ALL, 3)

        statColumnNameLabel = wx.StaticText(self, label = 'Status', style = wx.CENTER)
        statColumnNameLabel.SetFont(columnNameFont)
        rightColumn.Add(statColumnNameLabel, 0, wx.CENTER | wx.ALL, 3)

        for i in self.deviceList:
            deviceLabel = wx.StaticText(self, label = i[1], style = wx.CENTER)
            leftColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            leftColumn.Add(deviceLabel, 0, wx.EXPAND | wx.ALL, 3)

            statusLabel = wx.StaticText(self, label = 'Ready', style = wx.CENTER)
            rightColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            rightColumn.Add(statusLabel, 0, wx.EXPAND | wx.ALL, 3)
            self.statusLabels.append(statusLabel)

        mainSizer.Add(leftColumn, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND)
        mainSizer.Add(rightColumn, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(mainSizer)

    def installBuild(self, build):
        if not build.endswith('.apk'):
            errorDlg = wx.MessageDialog(self, "Please choose build!", 'Error!',
                                         style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        for i, j in zip(self.deviceList, self.statusLabels):
            thread = threading.Thread(target = self.installingThread, args = (i[0], build, j))
            thread.start()

    def installingThread(self, device, build, statusLabel):
        statusLabel.SetLabel('Installing...')
        statusLabel.SetLabel(self.adb.installBuild(device, build))

class FileDragAndDropHandler(wx.FileDropTarget):
    def __init__(self, target, parentPanel):
        wx.FileDropTarget.__init__(self)
        self.target = target
        self.parentPanel = parentPanel

    def OnDropFiles(self, x, y, filenames):
        extension = '.apk'
        if len(filenames) > 1:
            self.parentPanel.setBuild('', self.target)
            self.target.SetValue('Only 1 file at time is allowed!')
        else:
            if filenames[0].endswith(extension):
                self.parentPanel.setBuild(filenames[0], self.target)
            else:
                self.parentPanel.setBuild('', self.target)
                self.target.SetValue('Dropped file must end with {}'.format(extension))
        return True

class Adb():
    def __init__(self):
        pass

    @staticmethod
    def getListOfAttachedDevices():
        devices = []
        retries = 0
        while True:
            if retries > 4:
                break
            else:
                try:
                    _l = subprocess.check_output(r"adb devices", shell = True)
                    if "doesn't" in _l.decode():
                        retries += 1
                        continue
                    else:
                        break
                except subprocess.CalledProcessError:
                    retries += 1
                    continue
        rawList = _l.rsplit()
        tempList = rawList[4:]
        for i in range(len(tempList)):
            if i%2 == 0:
                devices.append((tempList[i].decode(), tempList[i+1].decode()))
        return devices
    
    @staticmethod
    def captureScreenshot(device, filename):
        dirOnDevice = os.path.join('sdcard/', filename)
        timeout = 10
        try:
            subprocess.check_output(r'adb -s {} shell screencap "{}"'.format(device, dirOnDevice), timeout = timeout)
            return ('Pulling file...', dirOnDevice)
        except subprocess.CalledProcessError:
            return ('An error occured while taking screenshot!', False)
        except subprocess.TimeoutExpired:
            return ('Timed out! ({}s)'.format(timeout), False)

    @staticmethod
    def pullScreenshot(device, fullPathOnDevice, destinationDirectory):
        timeout = 15
        try:
            subprocess.check_output(r'adb -s {} pull "{}" {}'.format(device, fullPathOnDevice, destinationDirectory))
            return 'Done!'
        except subprocess.CalledProcessError:
            return 'An error ocurred!'
        except subprocess.TimeoutExpired:
            return 'Timed out! ({}s)'.format(timeout)

    @staticmethod
    def installBuild(device, build):
        timeout = 60
        try:
            print('starting to install on {}'.format(device))
            raw_out = subprocess.check_output(r'adb -s {} install -r "{}"'.format(device, build), timeout = timeout)
            return 'Installed!'
        except subprocess.CalledProcessError:
            return 'Error!'
        except subprocess.TimeoutExpired:
            return 'Timed out! ({}s)'.format(timeout)

    @staticmethod
    def getDeviceIpAddress(device):
        try:
            raw = subprocess.check_output(r"adb -s {} shell ip addr show wlan0".format(device), shell = True).decode().split()
        except subprocess.CalledProcessError:
            return 'couldnt retrieve ip'
        for i in raw:
            if i[0:7] == '192.168':
                return i[0:len(i)-3]

    @staticmethod
    def getDeviceScreenSize(device):
        rawData = subprocess.check_output(r"adb -s {} shell wm size".format(device)).decode().split()
        res = re.sub('x', ' ', rawData[2]).split()
        return "{}x{}".format(res[1], res[0])

    @staticmethod
    def getBatteryStatus(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys battery'.format(device), shell = True).decode().split()
        for i in range(len(out)):
            if out[i] == 'level:':
                return out[i+1]+'%'

    @staticmethod
    def getPluggedInStatus(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys battery'.format(device), shell = True).decode().split()
        for i in range(len(out)):
            if out[i] == 'AC' or out[i] == 'USB':
                if out[i+2] == 'true':
                    return 'True, {} powered'.format(out[i])
        return 'False'

    @staticmethod
    def getOsVersion(device):
        return subprocess.check_output(r'adb -s {} shell getprop ro.build.version.release'.format(device), shell = True)

    @staticmethod
    def getApiVersion(device):
        return subprocess.check_output(r'adb -s {} shell getprop ro.build.version.sdk'.format(device), shell = True)

    @staticmethod
    def getDeviceModel(device):
        return subprocess.check_output(r'adb -s {} shell getprop ro.product.model'.format(device), shell = True).rstrip().decode()

    @staticmethod
    def getDeviceTimezone(device):
        return subprocess.check_output(r'adb -s {} shell getprop persist.sys.timezone'.format(device), shell = True)

    @staticmethod
    def getDeviceLanguage(device):
        lang = subprocess.check_output(r'adb -s {} shell getprop persist.sys.locale'.format(device), shell = True).rstrip()
        if len(lang) > 0:
            return lang
        else:
            return 'N/A'

    @staticmethod
    def getMarketingName(device):
        name = subprocess.check_output(r'adb -s {} shell getprop ro.config.marketing_name'.format(device), shell = True).rstrip()
        if len(name) > 0:
            return name
        else:
            return 'N/A'

    @staticmethod
    def getBrand(device):
        return subprocess.check_output(r'adb -s {} shell getprop ro.product.brand'.format(device), shell = True)

    @staticmethod
    def getWifiName(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys wifi'.format(device), shell = True).decode().split()
        for i in range(len(out)):
            if out[i] == 'mWifiInfo':
                return out[i+2][:-1]

    @staticmethod
    def getListOfHuuugePackages(device):
        packages = []
        list = ('huuuge', 'gamelion')
        output = subprocess.check_output(r'adb -s {} shell pm list packages'.format(device), shell = True).decode().split()
        for i in list:
            for j in output:
                if i in j:
                    packages.append(j)
        return packages[0][8:]
    
    @staticmethod
    def getTcpipPort(device):
        port = subprocess.check_output(r'adb -s {} shell getprop service.adb.tcp.port'.format(device), shell = True).rstrip()
        if len(port) > 0:
            return port
        else:
            return 'Not set'

    @staticmethod
    def getSerialNo(device):
        serial = subprocess.check_output(r'adb -s {} shell getprop ro.boot.serialno'.format(device), shell = True).rstrip()
        if len(serial) > 0:
            return serial
        else:
            return 'Not set'

if __name__ == '__main__':
    app = wx.App(False)
    MainFrame(None, 'ADB GUI')
    app.MainLoop()

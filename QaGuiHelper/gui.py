import glob
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
        self.mainFrame = wx.Frame.__init__(self, parent, title = title, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.optionsHandler = OptionsHandler()

        self.adb = Adb()

        mainSizer.Add(DevicesPanel(self, self.adb, self.optionsHandler), 1, wx.EXPAND)

        fileMenu = wx.Menu()
        options = fileMenu.Append(wx.ID_ANY, 'Options')
        fileMenu.AppendSeparator()
        ext = fileMenu.Append(wx.ID_ANY, 'Exit')

        jenkinsMenu = JenkinsMenu(self, 'links.json', self.optionsHandler)
            
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, 'File')
        menuBar.Append(jenkinsMenu, 'Jenkins')
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.showOptions, options)
        self.Bind(wx.EVT_MENU, self.onExit, ext)
        self.Bind(wx.EVT_CLOSE, self.onExit)

        self.SetSizer(mainSizer)
        self.Fit()
        self.Show(True)
        
    def onExit(self, event):
        self.optionsHandler.saveOptionsToFile()
        self.Destroy()

    def showOptions(self, event):
        disabler = wx.WindowDisabler()
        OptionsFrame(self, disabler, self.optionsHandler)

class OptionsHandler():
    def __init__(self):
        optionsPath = os.path.join(os.getenv('APPDATA'), 'adbgui')
        self.optionsFilePath = os.path.join(optionsPath, 'options.json')
        self.__optionsCategories = (
            ('Screenshots folder', 'folder'),
            ('Builds folder', 'folder'),
            ('Jenkins credentials', 'input'),
            ('Keep SS on device', 'checkbox')
        )
        self.__options = self.getOptionsIfAlreadyExist(optionsPath, self.optionsFilePath)

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
    def __init__(self, parent, pathToJsonFile, optionsHandler):
        wx.Menu.__init__(self)
        self.parent = parent
        self.optionsHandler = optionsHandler
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
            if len(self.optionsHandler.getOption('Jenkins credentials')) != 2:
                errorDlg = wx.MessageDialog(self.parent, 'Please provide your jenkins credentials (file -> options)', 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
                errorDlg.ShowModal()
                return
            buildInfo = RetrieveLinkDialog(self.parent, info, self.optionsHandler).getLink()
            DownloadBuildDialog(self.parent, buildInfo, self.optionsHandler).downloadBuild()
        return getBuildEvent

class OptionsFrame(wx.Frame):
    def __init__(self, parent, disabler, optionsHandler):
        wx.Frame.__init__(self, parent, title = 'Options', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.mainWindow = parent
        self.disabler = disabler
        self.panel = OptionsPanel(self, optionsHandler)
        self.bindEvents()
        self.Fit()
        self.Show(True)
    
    def bindEvents(self):
        self.Bind(wx.EVT_CLOSE, self.onClose)
    
    def onClose(self, event):
        del self.disabler
        self.Destroy()
        self.mainWindow.Raise()

class OptionsPanel(wx.Panel):
    def __init__(self, parent, optionsHandler):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.optionsHandler = optionsHandler
        self.changedOptions = {}
        self.createPanel()

    def createPanel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        first = True

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)

        saveBtn = wx.Button(self, wx.ID_ANY, 'Save')
        saveBtn.Disable()
        buttonsSizer.Add(saveBtn, 0, wx.CENTER | wx.ALL, 5)
        
        closeBtn = wx.Button(self, wx.ID_ANY, 'Close')
        buttonsSizer.Add(closeBtn, 0, wx.CENTER | wx.ALL, 5)

        for i, j in self.optionsHandler.getOptionsCategories():
            rowSizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label = i, style = wx.TE_CENTRE, size = (100, 10))
            rowSizer.Add(label, 0, wx.EXPAND | wx.TOP, 8)
            if not first:
                sizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 3)
            else:
                first = False
            if j == 'folder':
                valueCtrl = wx.TextCtrl(self, value = self.optionsHandler.getOption(i), size = (210, -1), style = wx.TE_READONLY)
                rowSizer.Add(valueCtrl, 0, wx.EXPAND | wx.ALL, 5)
                editBtn = wx.Button(self, wx.ID_ANY, 'Edit')
                rowSizer.Add(editBtn, 0, wx.EXPAND | wx.ALL, 5)
                self.Bind(wx.EVT_BUTTON, self.editFileOption(i, valueCtrl, saveBtn), editBtn)
            elif j == 'input':
                inputUsername = wx.TextCtrl(self, value = self.optionsHandler.getOption(i, True)[0], size = (100, -1), style = wx.TE_READONLY)
                rowSizer.Add(inputUsername, 0, wx.EXPAND | wx.ALL, 5)
                inputPassword = wx.TextCtrl(self, value = self.optionsHandler.getOption(i, True)[1], size = (100, -1), style = wx.TE_READONLY)
                rowSizer.Add(inputPassword, 0, wx.EXPAND | wx.ALL, 5)
                editBtn = wx.Button(self, wx.ID_ANY, 'Edit')
                rowSizer.Add(editBtn, 0, wx.EXPAND | wx.ALL, 5)
                self.Bind(wx.EVT_BUTTON, self.editCredentialsOption((inputUsername, inputPassword), saveBtn), editBtn)
            elif j == 'checkbox':
                checkboxCtrl = wx.CheckBox(self, style = wx.CENTER)
                checkboxCtrl.SetValue(self.optionsHandler.getOption(i))
                rowSizer.Add(checkboxCtrl, 0, wx.EXPAND | wx.ALL, 5)
                self.Bind(wx.EVT_CHECKBOX, self.onSwitchCheckbox(i, checkboxCtrl, saveBtn), checkboxCtrl)
            sizer.Add(rowSizer, 0, wx.CENTER | wx.ALL, 5)
        
        sizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(buttonsSizer, 0, wx.CENTER | wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self.saveChanges(saveBtn), saveBtn)
        self.Bind(wx.EVT_BUTTON, self.parent.onClose, closeBtn)
        
        self.SetSizer(sizer)
        self.Fit()

    def onSwitchCheckbox(self, option, checkboxCtrl, saveBtn):
        def onSwitchCheckboxEvent(event):
            self.onChangedOption(option, checkboxCtrl.GetValue(), saveBtn)
        return onSwitchCheckboxEvent

    def saveChanges(self, btn):
        def saveChangesEvent(event):
            for i in self.changedOptions.keys():
                self.optionsHandler.setOption(i, self.changedOptions[i])
            btn.Disable()
        return saveChangesEvent

    def editFileOption(self, option, valueControl, saveBtn):
        def editOptionEvent(event):
            with wx.DirDialog(self, 'Choose {} path'.format(option)) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    newOption = dlg.GetPath()
                    self.onChangedOption(option, newOption, saveBtn, valueControl)
        return editOptionEvent

    def onChangedOption(self, option, value, saveBtn, textCtrl = None):
        self.changedOptions[option] = value
        if isinstance(textCtrl, wx.TextCtrl):
            textCtrl.SetValue(value)
        elif isinstance(textCtrl, list) or isinstance(textCtrl, tuple):
            for i, j in zip(textCtrl, value):
                i.SetValue(j)
        else:
            pass #checkbox case
        saveBtn.Enable()

    def editCredentialsOption(self, jenkinsCredentialControls, saveBtn):
        def editCredentialsOptionEvent(event):
            disabler = wx.WindowDisabler()
            JenkinsCredentialsEditFrame(self, self.optionsHandler, disabler, self.onChangedOption, saveBtn, jenkinsCredentialControls)
        return editCredentialsOptionEvent

class JenkinsCredentialsEditFrame(wx.Frame):
    def __init__(self, parent, optionsHandler, disabler, onChangedOptionFunc, saveBtn, jenkinsCredentialControls):
        wx.Frame.__init__(self, parent, title = 'Edit credentials', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.parent = parent
        self.disabler = disabler
        self.panel = JenkinsCredentialsEditPanel(self, optionsHandler, onChangedOptionFunc, saveBtn, jenkinsCredentialControls)
        self.bindEvents()
        self.Fit()
        self.Show(True)
    
    def bindEvents(self):
        self.Bind(wx.EVT_CLOSE, self.onClose())

    def onClose(self):
        def onCloseEvent(event):
            del self.disabler
            self.Destroy()
            self.parent.Raise()
        return onCloseEvent

class JenkinsCredentialsEditPanel(wx.Panel):
    def __init__(self, parent, optionsHandler, onChangedOptionFunc, saveBtn, jenkinsCredentialControls):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.saveBtn = saveBtn
        self.optionsHandler = optionsHandler
        self.onChangedOptionFunc = onChangedOptionFunc
        self.jenkinsCredentialControls = jenkinsCredentialControls
        self.createPanel()

    def createPanel(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        topSizer = wx.BoxSizer(wx.HORIZONTAL)

        userSizer = wx.BoxSizer(wx.VERTICAL)
        userLabel = wx.StaticText(self, label = 'User')
        userSizer.Add(userLabel, 0, wx.CENTER | wx.ALL, 3)
        userInputField = wx.TextCtrl(self, size = (100, -1))
        userSizer.Add(userInputField, 0, wx.ALL, 3)

        passwordSizer = wx.BoxSizer(wx.VERTICAL)
        passwordLabel = wx.StaticText(self, label = 'Password')
        passwordSizer.Add(passwordLabel, 0, wx.CENTER | wx.ALL, 3)
        passwordInputField = wx.TextCtrl(self, size = (100, -1))
        passwordSizer.Add(passwordInputField, 0, wx.ALL, 3)

        topSizer.Add(userSizer, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 3)
        topSizer.Add(passwordSizer, 0, wx.EXPAND | wx.ALL, 5)

        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        saveBtn = wx.Button(self, wx.ID_ANY, 'Update')
        self.Bind(wx.EVT_BUTTON, self.updateJenkinsCreds(userInputField, passwordInputField), saveBtn)
        bottomSizer.Add(saveBtn, 0, wx.CENTER | wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 10)

        mainSizer.Add(topSizer, 0)
        mainSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(bottomSizer, 0, wx.CENTER)
        self.SetSizer(mainSizer)
        self.Fit()

    def updateJenkinsCreds(self, usernameInputField, passwordInputField):
        def updateJenkinsCredsEvent(event):
            newCreds = (usernameInputField.GetValue(), passwordInputField.GetValue())
            self.onChangedOptionFunc(self.optionsHandler.getOptionsCategories()[2][0], newCreds, self.saveBtn, self.jenkinsCredentialControls)
            del self.parent.disabler
            #hackish way to do it - TODO: implement it in some elegant way
            self.parent.Destroy()
            self.parent.parent.Raise()
        return updateJenkinsCredsEvent

class RetrieveLinkDialog(wx.GenericProgressDialog):
    def __init__(self, parent, info, optionsHandler):
        wx.GenericProgressDialog.__init__(self, 'Working...', 'Retrieving build information...', style = wx.PD_APP_MODAL)
        self.parent = parent
        self.optionsHandler = optionsHandler
        self.info = info
        self.auth = self.optionsHandler.getOption('Jenkins credentials')

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
    def __init__(self, parent, info, optionsHandler):
        self.parent = parent
        self.info = info
        self.optionsHandler = optionsHandler
        self.dlg = wx.GenericProgressDialog.__init__(self, 'Downloading build!', self.info[0][1])

    def downloadBuild(self):
        buildFolder = self.optionsHandler.getOption('Builds folder')
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
    def __init__(self, parent, adb, optionsHandler):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.adb = adb
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent, self.adb)
        self.buttonsPanel = RefreshButtonPanel(self, self.parent, self.adb, optionsHandler)

        self.sizer.Add(self.buttonsPanel, 0, wx.EXPAND | wx.ALL, 15)
        self.sizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 6)
        self.sizer.Add(self.checkBoxesPanel, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(self.sizer)
        self.Fit()
    
    def refreshCheckboxesPanel(self):
        self.checkBoxesPanel.Destroy()
        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent, self.adb)
        self.sizer.Add(self.checkBoxesPanel, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)
        self.Layout()
        self.Fit()
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
            infoButton = wx.Button(self, label = 'i', style = wx.CENTER, size = (20, 5))

            leftColumn.Add(modelLabel, 1, wx.CENTER | wx.ALL, 9)
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
    def __init__(self, parent, mainWindow, adb, optionsHandler):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.adb = adb
        self.optionsHandler = optionsHandler
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
        ssFolder = self.optionsHandler.getOption('Screenshots folder')
        if (len(devices)) == 0:
            errorDlg = wx.MessageDialog(self.parent, 'At least 1 device must be selected!', 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        if not os.path.exists(ssFolder):
            time.sleep(0.2)
            errorDlg = wx.MessageDialog(self.parent, "Save screenshots directory doesn't exist! Set it in Options -> Screenshots Folder", 'Error!',
                                         style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        disabler = wx.WindowDisabler()
        ScreenshotCaptureFrame(self, self.mainWindow, disabler, self.adb, devices, ssFolder)

    def refreshDevicesPanel(self, event):
        self.parent.refreshCheckboxesPanel()
    
    def installBuild(self, event):
        devices = self.parent.checkBoxesPanel.getCheckedDevices()
        if (len(devices)) == 0:
            errorDlg = wx.MessageDialog(self.parent, 'At least 1 device must be selected!', 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        disabler = wx.WindowDisabler()
        BuildInstallerFrame(self.mainWindow, disabler, self.adb, devices, self.optionsHandler)

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
        wx.Frame.__init__(self, parent, title = 'Device Info', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
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
        self.mainWindow.Raise()

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
            pass

class ScreenshotCaptureFrame(wx.Frame):
    def __init__(self, parent, mainWindow, disabler, adb, listOfDevices, ssFolder):
        self.frame = wx.Frame.__init__(self, mainWindow, title = 'Capturing screenshots!', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.disabler = disabler
        self.mainWindow = mainWindow

        self.panel = ScreenshotCapturePanel(self, adb, listOfDevices, ssFolder)
        self.bindEvents()
        self.Fit()
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
        self.parent = parent
        self.adb = adb
        self.directoryForScreenshots = directoryForScreenshots
        self.listOfDevices = listOfDevices
        self.buttons = []
        self.statusLabels = []
        self.createControls()
        self.deployScreenshotThreads()

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        listSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftColumn = wx.BoxSizer(wx.VERTICAL)
        rightColumn = wx.BoxSizer(wx.VERTICAL)
        columnNameFont = wx.Font(14, wx.MODERN, wx.ITALIC, wx.LIGHT)

        devColumnNameLabel = wx.StaticText(self, label = 'Device', style = wx.CENTER)
        devColumnNameLabel.SetFont(columnNameFont)
        leftColumn.Add(devColumnNameLabel, 0, wx.CENTER | wx.ALL, 3)

        statColumnNameLabel = wx.StaticText(self, label = 'Status', style = wx.CENTER)
        statColumnNameLabel.SetFont(columnNameFont)
        rightColumn.Add(statColumnNameLabel, 0, wx.CENTER | wx.ALL, 3)

        for i in self.listOfDevices:
            deviceLabel = wx.StaticText(self, label = i[1], style = wx.CENTER)
            leftColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            leftColumn.Add(deviceLabel, 0, wx.EXPAND | wx.CENTER | wx.ALL, 10)

            statusLabel = wx.StaticText(self, label = 'Ready', style = wx.CENTER)
            rightColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            rightColumn.Add(statusLabel, 0, wx.EXPAND | wx.CENTER | wx.ALL, 10)
            self.statusLabels.append(statusLabel)

        listSizer.Add(leftColumn, 1, wx.EXPAND | wx.CENTER | wx.ALL, 5)
        listSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5)
        listSizer.Add(rightColumn, 1, wx.EXPAND | wx.CENTER | wx.ALL, 5)

        mainSizer.Add(listSizer, 2, wx.EXPAND | wx.ALL, 5)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        openButton = wx.Button(self, wx.ID_ANY, 'Open Folder')
        openButton.Disable()
        self.buttons.append(openButton)
        buttonSizer.Add(openButton, 1, wx.EXPAND | wx.ALL, 3)
        closeButton = wx.Button(self, wx.ID_ANY, 'Close')
        closeButton.Disable()
        self.buttons.append(closeButton)
        buttonSizer.Add(closeButton, 1, wx.EXPAND | wx.ALL, 3)

        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self.openScreenshotsFolder, openButton)
        self.Bind(wx.EVT_BUTTON, self.parent.onClose, closeButton)

        self.SetSizer(mainSizer)
        self.Fit()

    def deployScreenshotThreads(self):
        buttonUnlocker = ButtonUnlocker(len(self.listOfDevices), self.buttons)
        for i, j in zip(self.listOfDevices, self.statusLabels):
            localThread = threading.Thread(target = self.captureAndPullScreenshot, args = (i[0], self.directoryForScreenshots, j, i[1], buttonUnlocker))
            localThread.start()
        
    def captureAndPullScreenshot(self, device, directory, statusLabel, model, buttonUnlocker):
        statusLabel.SetLabel('Taking screenshot...')
        pathToScreenOnDevice = ''
        rawFileName = self.getFileName(device, model)
        indexedFileName = self.getFileNameWithIndex(rawFileName, directory)
        clbk = self.adb.captureScreenshot(device, indexedFileName)
        try:
            statusLabel.SetLabel(clbk[0])
        except RuntimeError:
            return
        if not clbk[1]:
            buttonUnlocker.finishThread()
            return
        pathToScreenOnDevice = clbk[1]
        clbk = self.adb.pullScreenshot(device, pathToScreenOnDevice, directory)
        try:            
            statusLabel.SetLabel(clbk)
            buttonUnlocker.finishThread()
        except RuntimeError:
            return

    def getFileNameWithIndex(self, rawFileName, directory):
        currentlyExistingFiles = glob.glob(os.path.join(directory, '{}*'.format(rawFileName)))
        if len(currentlyExistingFiles) > 0:
            lastIndex = self.getNextIndexOfFile(max(currentlyExistingFiles, key = self.getIndexOfFile))
            fileName = '{}_{}.png'.format(rawFileName, lastIndex)
            return fileName
        else:
            fileName = '{}_1.png'.format(rawFileName)
            return fileName
    
    def getIndexOfFile(self, f):
        return int(f[f.find('_')+1:f.find('.png')])

    def getNextIndexOfFile(self, f):
        return int(f[f.find('_')+1:f.find('.png')])+1

    def getFileName(self, device, model):
        unsupportedChars = (' ', '(', ')', '_')
        for i in unsupportedChars:
            model = model.replace(i, '')
        deviceScreenSize = self.adb.getDeviceScreenSize(device)
        return '{}-{}'.format(model, deviceScreenSize)

    def openScreenshotsFolder(self, event):
        os.startfile(self.directoryForScreenshots)

class ButtonUnlocker():
    def __init__(self, count, btns):
        self.count = count
        self.semph = threading.Semaphore()
        self.buttons = btns

    def finishThread(self):
        self.semph.acquire()
        try:
            self.count -= 1
            if self.count == 0:
                for i in self.buttons:
                    i.Enable()
        finally:
            self.semph.release()

class BuildInstallerFrame(wx.Frame):
    def __init__(self, mainWindow, disabler, adb, deviceList, optionsHandler):
        wx.Frame.__init__(self, mainWindow, title = 'Installing builds', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.disabler = disabler
        self.mainWindow = mainWindow

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.topPanel = BuildInstallerTopPanel(self, optionsHandler.getOption('Builds folder'))
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
        self.installBuildBtn = None
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

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.installBuildBtn = wx.Button(self, wx.ID_ANY, 'Install')
        buttonsSizer.Add(self.installBuildBtn, 0, wx.EXPAND | wx.ALL, 3)
        optionsComboBox = wx.ComboBox(self, wx.ID_ANY, value = 'Clean', choices = ('Clean', 'Overwrite'), style = wx.CB_READONLY)
        buttonsSizer.Add(optionsComboBox, 0, wx.EXPAND | wx.ALL, 3)
        mainSizer.Add(buttonsSizer, 0, wx.CENTRE | wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self.startInstallingBuild(optionsComboBox), self.installBuildBtn)
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
            builds = glob.glob(os.path.join(self.buildFolder, '*.apk'))
            latestBuild = max(builds, key = os.path.getctime)
            self.setBuild(latestBuild, textCtrl)
        return getLatestBuildFromOptionsFolderEvent
    
    def setBuild(self, build, textCtrl):
        self.buildChosen = build
        textCtrl.SetValue(build)

    def startInstallingBuild(self, comboBoxCtrl):
        def startInstallingBuildEvent(event):
            self.parent.bottomPanel.installBuild(self.buildChosen, comboBoxCtrl.GetStringSelection())
        return startInstallingBuildEvent

class BuildInstallerBottomPanel(wx.Panel):
    def __init__(self, parent, deviceList, adb):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.listOfDevices = deviceList
        self.adb = adb
        self.statusLabels = []
        self.buttons = []
        self.createControls()
        self.Fit()

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        columnsSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftColumn = wx.BoxSizer(wx.VERTICAL)
        rightColumn = wx.BoxSizer(wx.VERTICAL)
        columnNameFont = wx.Font(14, wx.MODERN, wx.ITALIC, wx.LIGHT)

        devColumnNameLabel = wx.StaticText(self, label = 'Device', style = wx.CENTER)
        devColumnNameLabel.SetFont(columnNameFont)
        leftColumn.Add(devColumnNameLabel, 0, wx.CENTER | wx.ALL, 3)

        statColumnNameLabel = wx.StaticText(self, label = 'Status', style = wx.CENTER)
        statColumnNameLabel.SetFont(columnNameFont)
        rightColumn.Add(statColumnNameLabel, 0, wx.CENTER | wx.ALL, 3)

        for i in self.listOfDevices:
            deviceLabel = wx.StaticText(self, label = i[1], style = wx.CENTER)
            leftColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            leftColumn.Add(deviceLabel, 0, wx.EXPAND | wx.ALL, 3)

            statusLabel = wx.StaticText(self, label = 'Ready', style = wx.CENTER)
            rightColumn.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            rightColumn.Add(statusLabel, 0, wx.EXPAND | wx.ALL, 3)
            self.statusLabels.append(statusLabel)

        columnsSizer.Add(leftColumn, 1, wx.EXPAND | wx.ALL, 5)
        columnsSizer.Add(wx.StaticLine(self, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND)
        columnsSizer.Add(rightColumn, 1, wx.EXPAND | wx.ALL, 5)

        self.closeBtn = wx.Button(self, wx.ID_ANY, 'Close')
        self.Bind(wx.EVT_BUTTON, self.parent.onClose, self.closeBtn)
        self.buttons.append(self.closeBtn)
        self.buttons.append(self.parent.topPanel.installBuildBtn)

        mainSizer.Add(columnsSizer, 0, wx.EXPAND)
        mainSizer.Add(self.closeBtn, 0, wx.CENTER | wx.ALL, 5)
        
        self.SetSizer(mainSizer)

    def installBuild(self, build, option):
        if not build.endswith('.apk'):
            errorDlg = wx.MessageDialog(self, "Please choose build!", 'Error!',
                                         style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        for i in self.buttons:
            i.Disable()
        buttonUnlocker = ButtonUnlocker(len(self.listOfDevices), self.buttons)
        for i, j in zip(self.listOfDevices, self.statusLabels):
            thread = threading.Thread(target = self.installingThread, args = (i[0], build, j, option, buttonUnlocker))
            thread.start()

    def installingThread(self, device, build, statusLabel, option, buttonUnlocker):
        buildPackage = self.adb.getPackageNameOfAppFromApk(build)
        buildVer = self.adb.getBuildVersionFromApk(build)
        if option == 'Clean':
            statusLabel.SetLabel('Checking if exists...'.format(buildPackage))
            if self.adb.isBuildIsAlreadyInstalled(device, buildPackage):
                statusLabel.SetLabel('Build exists!'.format(buildPackage))
                time.sleep(1)
                statusLabel.SetLabel('Checking version...')
                time.sleep(1)
                if self.adb.getBuildVersionFromDevice(device, buildPackage) == buildVer:
                    statusLabel.SetLabel('Versions match!')
                    time.sleep(1)
                    statusLabel.SetLabel('Checking type...')
                    if self.adb.isApkDebuggable(build) == self.adb.isInstalledPackageDebuggable(device, buildPackage):
                        statusLabel.SetLabel('Types match!')
                        time.sleep(1)
                        statusLabel.SetLabel('Removing local data...')
                        time.sleep(1)
                        if self.adb.removeLocalAppData(device, buildPackage):
                            statusLabel.SetLabel('Done!')
                            buttonUnlocker.finishThread()
                            return
                    else:
                        statusLabel.SetLabel('Types dont match...')
                        time.sleep(1)
                else:
                    statusLabel.SetLabel('Versions dont match')
                time.sleep(1)
                statusLabel.SetLabel('Uninstalling {}'.format(buildPackage))
                time.sleep(1)
                clbk = self.adb.uninstallApp(device, buildPackage)
                statusLabel.SetLabel(clbk)
            else:
                statusLabel.SetLabel('Build not installed.')
        elif option == 'Overwrite':
            buildVerNumerizedOnApk = int(buildVer.split('.')[-1])
            buildVerNumerizedOnDev = int(self.adb.getBuildVersionFromDevice(device, buildPackage).split('.')[-1])
            if buildVerNumerizedOnDev > buildVerNumerizedOnApk:
                statusLabel.SetLabel('Error downgrade!')
                buttonUnlocker.finishThread()
                return
        time.sleep(1)
        statusLabel.SetLabel('Installing...')
        if self.adb.installBuild(device, build):
            statusLabel.SetLabel('Done!')
        else:
            statusLabel.SetLabel('An error occured.')
        buttonUnlocker.finishThread()
        return

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
    def uninstallApp(device, pckg):
        try:
            subprocess.check_output(r'adb -s {} uninstall {}'.format(device, pckg))
            return 'Done!'
        except subprocess.CalledProcessError:
            return 'An error occured.'

    @staticmethod
    def isApkDebuggable(build):
        try:
            out = subprocess.check_output(r'aapt dump badging {}'.format(build)).decode().split()
            for i in out:
                if 'application-debuggable' in i:                    
                    return True
            return False
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return 'Aapt not found.'

    @staticmethod
    def isInstalledPackageDebuggable(device, pckg):
        try:
            out = subprocess.check_output(r'adb -s {} shell dumpsys package {}'.format(device, pckg)).decode().rsplit('\n')
            for i in [j.replace(' ', '') for j in out]:
                if 'flags' in i:
                    if 'DEBUG' in i:
                        return True
            return False
        except subprocess.CalledProcessError:
            return
    
    @staticmethod
    def removeLocalAppData(device, pckg):
        try:
            subprocess.check_output(r'adb -s {} shell pm clear {}'.format(device, pckg))
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def isBuildIsAlreadyInstalled(device, pckg):
        try:
            out = subprocess.check_output(r'adb -s {} shell pm list packages'.format(device)).decode().split()
            for i in out:
                if pckg in i:
                    return True
            return False
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def getPackageNameOfAppFromApk(build):
        try:
            out = subprocess.check_output(r'aapt dump badging {}'.format(build)).decode().split()
            for i in out:
                if 'com.' in i:
                    packageName = i[i.find('com.'):-1]
                    return packageName
        except FileNotFoundError:
            return 'Aapt not found.'
        except subprocess.CalledProcessError:
            return 'An error occured.'

    @staticmethod
    def getBuildVersionFromApk(build):
        try:
            out = subprocess.check_output(r'aapt dump badging {}'.format(build)).decode().split()
            for i in out:
                if 'versionName' in i:
                    return i[i.find('=')+2:-1]
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return 'Aapt not found.'

    @staticmethod
    def getBuildVersionFromDevice(device, pckg):
        try:
            out = subprocess.check_output(r'adb -s {} shell dumpsys package {}'.format(device, pckg)).decode().split()
            for i in out:
                if 'versionName' in i:
                    return i[i.find('=')+1:]
            return False
        except subprocess.CalledProcessError:
            return False

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
        for idx, i in enumerate(tempList):
            if idx%2 == 0:
                devices.append((i.decode(), tempList[idx+1].decode()))
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
            raw_out = subprocess.check_output(r'adb -s {} install -r "{}"'.format(device, build), timeout = timeout)
            return True
        except subprocess.CalledProcessError:
            return False
        except subprocess.TimeoutExpired:
            return False

    @staticmethod
    def getDeviceIpAddress(device):
        try:
            raw = subprocess.check_output(r"adb -s {} shell ip addr show wlan0".format(device), shell = True).decode().split()
        except subprocess.CalledProcessError:
            return 'couldnt retrieve ip'
        for i in raw:
            if i[0:7] == '192.168':
                return i[0:len(i)-3]
        return 'Not set'

    @staticmethod
    def getDeviceScreenSize(device):
        rawData = subprocess.check_output(r"adb -s {} shell wm size".format(device)).decode().split()
        res = re.sub('x', ' ', rawData[2]).split()
        return "{}x{}".format(res[1], res[0])

    @staticmethod
    def getBatteryStatus(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys battery'.format(device), shell = True).decode().split()
        for idx, i in enumerate(out):
            if i == 'level:':
                return out[idx+1]+'%'

    @staticmethod
    def getPluggedInStatus(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys battery'.format(device), shell = True).decode().split()
        for idx, i in enumerate(out):
            if i == 'AC' or i == 'USB':
                if out[idx+2] == 'true':
                    return 'True, {} powered'.format(i)
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
        for idx, i in enumerate(out):
            if i == 'mWifiInfo':
                if out[idx+2][1:] == 'unknown':
                    return 'Not set'
                else:
                    return out[idx+2][:-1]

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

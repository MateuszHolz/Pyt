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
        OptionsFrame(self, self.optionsHandler)

    def showInfoAboutDevice(self, event):
        deviceId, state = event.GetEventObject().info
        if state == 'unauthorized':
            errorDlg = wx.MessageDialog(self, "Unauthorized device! Check authorization dialog on device.", 'Unauthorized device!',
                                        style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        DeviceInfoFrame(self, deviceId, self.adb)

class OptionsFrame(wx.Frame):
    def __init__(self, mainFrame, optionsHandler):
        wx.Frame.__init__(self, mainFrame, title = 'Options', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.disabler = wx.WindowDisabler(self)
        self.mainFrame = mainFrame
        self.optionsHandler = optionsHandler
        self.changedOptions = {}
        self.panel = wx.Panel(self)
        self.saveBtn, self.jenkinsCredentialControls = self.createControls()
        self.Bind(wx.EVT_BUTTON, self.saveChanges, self.saveBtn)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Fit()
        self.Show(True)

    def createControls(self):
        jenkinsCredentialsControls = []
        sizer = wx.BoxSizer(wx.VERTICAL)
        first = True

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)

        saveBtn = wx.Button(self.panel, wx.ID_ANY, 'Save')
        saveBtn.Disable()
        buttonsSizer.Add(saveBtn, 0, wx.CENTER | wx.ALL, 5)
        
        closeBtn = wx.Button(self.panel, wx.ID_ANY, 'Close')
        buttonsSizer.Add(closeBtn, 0, wx.CENTER | wx.ALL, 5)

        for i, j in self.optionsHandler.getOptionsCategories():
            rowSizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self.panel, label = i, style = wx.TE_CENTRE, size = (150, 10))
            rowSizer.Add(label, 0, wx.EXPAND | wx.TOP, 8)
            if not first:
                sizer.Add(wx.StaticLine(self.panel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 3)
            else:
                first = False
            if j == 'folder':
                valueCtrl = wx.TextCtrl(self.panel, value = self.optionsHandler.getOption(i, str), size = (210, -1), style = wx.TE_READONLY)
                rowSizer.Add(valueCtrl, 0, wx.EXPAND | wx.ALL, 5)
                editBtn = wx.Button(self.panel, wx.ID_ANY, 'Edit')
                editBtn.info = i, valueCtrl
                rowSizer.Add(editBtn, 0, wx.EXPAND | wx.ALL, 5)
                self.Bind(wx.EVT_BUTTON, self.editFileOption, editBtn)
            elif j == 'input':
                inputUsername = wx.TextCtrl(self.panel, value = self.optionsHandler.getOption(i, tuple)[0], size = (100, -1), style = wx.TE_READONLY)
                jenkinsCredentialsControls.append(inputUsername)
                rowSizer.Add(inputUsername, 0, wx.EXPAND | wx.ALL, 5)
                inputPassword = wx.TextCtrl(self.panel, value = self.optionsHandler.getOption(i, tuple)[1], size = (100, -1), style = wx.TE_READONLY)
                jenkinsCredentialsControls.append(inputPassword)
                rowSizer.Add(inputPassword, 0, wx.EXPAND | wx.ALL, 5)
                editBtn = wx.Button(self.panel, wx.ID_ANY, 'Edit')
                rowSizer.Add(editBtn, 0, wx.EXPAND | wx.ALL, 5)
                self.Bind(wx.EVT_BUTTON, self.editCredentialsOption, editBtn)
            elif j == 'checkbox':
                checkboxCtrl = wx.CheckBox(self.panel, style = wx.CENTER)
                checkboxCtrl.SetValue(self.optionsHandler.getOption(i, bool))
                checkboxCtrl.info = i
                rowSizer.Add(checkboxCtrl, 0, wx.EXPAND | wx.ALL, 5)
                self.Bind(wx.EVT_CHECKBOX, self.onSwitchCheckbox, checkboxCtrl)
            sizer.Add(rowSizer, 0, wx.CENTER | wx.ALL, 5)
        
        sizer.Add(wx.StaticLine(self.panel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(buttonsSizer, 0, wx.CENTER | wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self.onClose, closeBtn)
        
        self.panel.SetSizer(sizer)
        self.panel.Fit()

        return saveBtn, jenkinsCredentialsControls

    ### EVENTS ###

    def onChangedOption(self, option, value, textCtrl = None):
        self.changedOptions[option] = value
        if isinstance(textCtrl, wx.TextCtrl):
            textCtrl.SetValue(value)
        elif isinstance(textCtrl, list) or isinstance(textCtrl, tuple):
            for i, j in zip(textCtrl, value):
                i.SetValue(j)
        else:
            pass #checkbox case
        self.saveBtn.Enable()

    def saveChanges(self, event):
        for i in self.changedOptions.keys():
            self.optionsHandler.setOption(i, self.changedOptions[i])
            event.GetEventObject().Disable()

    def editFileOption(self, event):
        option, valueCtrl = event.GetEventObject().info
        with wx.DirDialog(self, 'Choose {} path'.format(option)) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                newValue = dlg.GetPath()
                self.onChangedOption(option, newValue, valueCtrl)

    def editCredentialsOption(self, event):
        JenkinsCredentialsEditFrame(self, self.optionsHandler, self.jenkinsCredentialControls)

    def onSwitchCheckbox(self, event):
        option = event.GetEventObject().info
        self.onChangedOption(option, event.GetEventObject().GetValue(), None)

    def onClose(self, event):
        del self.disabler
        self.mainFrame.Raise()
        self.Destroy()

class JenkinsCredentialsEditFrame(wx.Frame):
    def __init__(self, parentFrame, optionsHandler, jenkinsCredentialControls):
        wx.Frame.__init__(self, parentFrame, title = 'Edit credentials', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.parentFrame = parentFrame
        self.optionsHandler = optionsHandler
        self.jenkinsCredentialControls = jenkinsCredentialControls
        self.disabler = wx.WindowDisabler(self)
        self.panel = wx.Panel(self)
        self.saveBtn, self.userInputField, self.passwordInputField = self.createControls()

        self.Bind(wx.EVT_BUTTON, self.updateJenkinsCreds, self.saveBtn)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Fit()
        self.Show(True)

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        topSizer = wx.BoxSizer(wx.HORIZONTAL)

        userSizer = wx.BoxSizer(wx.VERTICAL)
        userLabel = wx.StaticText(self.panel, label = 'User')
        userSizer.Add(userLabel, 0, wx.CENTER | wx.ALL, 3)
        userInputField = wx.TextCtrl(self.panel, size = (100, -1))
        userSizer.Add(userInputField, 0, wx.ALL, 3)

        passwordSizer = wx.BoxSizer(wx.VERTICAL)
        passwordLabel = wx.StaticText(self.panel, label = 'Password')
        passwordSizer.Add(passwordLabel, 0, wx.CENTER | wx.ALL, 3)
        passwordInputField = wx.TextCtrl(self.panel, size = (100, -1))
        passwordSizer.Add(passwordInputField, 0, wx.ALL, 3)

        topSizer.Add(userSizer, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(wx.StaticLine(self.panel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 3)
        topSizer.Add(passwordSizer, 0, wx.EXPAND | wx.ALL, 5)

        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        saveBtn = wx.Button(self.panel, wx.ID_ANY, 'Update')
        bottomSizer.Add(saveBtn, 0, wx.CENTER | wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 10)

        mainSizer.Add(topSizer, 0)
        mainSizer.Add(wx.StaticLine(self.panel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(bottomSizer, 0, wx.CENTER)
        self.panel.SetSizer(mainSizer)
        self.panel.Fit()

        return saveBtn, userInputField, passwordInputField
    
    ### EVENTS ###

    def updateJenkinsCreds(self, event):
        newCreds = self.userInputField.GetValue(), self.passwordInputField.GetValue()
        self.parentFrame.onChangedOption(self.optionsHandler.getOptionsCategories()[2][0], newCreds, self.jenkinsCredentialControls)
        self.Close()

    def onClose(self, event):
        del self.disabler
        self.parentFrame.Raise()
        self.Destroy()

class DeviceInfoFrame(wx.Frame):
    def __init__(self, parentFrame, deviceId, adb):
        wx.Frame.__init__(self, parentFrame, title = 'Device Info', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.parentFrame = parentFrame
        self.deviceId = deviceId
        self.adb = adb
        self.disabler = wx.WindowDisabler(self)
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
        self.panel = wx.Panel(self)
        self.deviceInfoControls = self.createControls()
        self.updateFields()
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Fit()
        self.Show(True)

    def createControls(self):
        deviceInfoControls = []
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        first = True
        for i in self.deviceInfoTable:
            if first:
                first = False
            else:
                mainSizer.Add(wx.StaticLine(self.panel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self.panel, label = i[0], size = (100, -1), style = wx.TE_CENTRE)
            sizer.Add(label, 0, wx.EXPAND | wx.TOP, label.GetSize()[1]/3.5)
            content = wx.TextCtrl(self.panel, value = '...', size = (150, -1), style = wx.TE_READONLY)
            deviceInfoControls.append(content)
            sizer.Add(content, 0, wx.ALIGN_RIGHT)
            mainSizer.Add(sizer, 0, wx.ALL, 5)
        self.panel.SetSizer(mainSizer)
        self.panel.Fit()

        return deviceInfoControls

    def updateFields(self):
        for func, ctrl in zip(self.deviceInfoTable, self.deviceInfoControls):
            localThread = threading.Thread(target = self.updateSingleControl, args = (ctrl, func[1]))
            localThread.start()

    def updateSingleControl(self, textCtrl, functionToCall):
        try:
            textCtrl.SetValue(functionToCall(self.deviceId))
        except RuntimeError:
            pass

    ### EVENTS ###

    def onClose(self, event):
        del self.disabler
        self.Destroy()
        self.parentFrame.Raise()

class ScreenshotCaptureFrame(wx.Frame):
    def __init__(self, mainFrame, adb, optionsHandler):
        wx.Frame.__init__(self, mainFrame, title = 'Capturing screenshots!', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.mainFrame = mainFrame
        self.adb = adb
        self.optionsHandler = optionsHandler
        self.checkboxesState = True
        self.directory = self.optionsHandler.getOption('Screenshots folder', str)
        self.disabler = wx.WindowDisabler(self)
        self.panel = wx.Panel(self)

        self.openButton, self.closeButton, self.captureButton, self.checkAllButton, self.devicesSizer = self.createControls()

        self.Bind(wx.EVT_BUTTON, self.switchAllCheckboxes, self.checkAllButton)
        self.Bind(wx.EVT_BUTTON, self.captureScreenshots, self.captureButton)
        self.Bind(wx.EVT_BUTTON, self.openScreenshotsFolder, self.openButton)
        self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Fit()
        self.Show(True)

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        devicesList = self.adb.getListOfAttachedDevices()
        devicesSizer = AuthorizedDevicesSizer(self.panel, devicesList, self.adb)
        mainSizer.Add(devicesSizer, 2, wx.EXPAND | wx.ALL, 5)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        captureButton = wx.Button(self.panel, wx.ID_ANY, 'Capture')
        buttonSizer.Add(captureButton, 0, wx.EXPAND | wx.ALL, 3)

        openButton = wx.Button(self.panel, wx.ID_ANY, 'Open Folder')
        buttonSizer.Add(openButton, 0, wx.EXPAND | wx.ALL, 3)

        checkAllButton = wx.Button(self.panel, wx.ID_ANY, 'Check all')
        buttonSizer.Add(checkAllButton, 0, wx.EXPAND | wx.ALL, 3)

        closeButton = wx.Button(self.panel, wx.ID_ANY, 'Close')
        buttonSizer.Add(closeButton, 0, wx.EXPAND | wx.ALL, 3)

        mainSizer.Add(buttonSizer, 0, wx.CENTER | wx.ALL, 5)

        self.panel.SetSizer(mainSizer)
        self.panel.Fit()

        return openButton, closeButton, captureButton, checkAllButton, devicesSizer

    def captureScreenshots(self, event):
        checkedDevices = self.devicesSizer.getCheckedDevices()
        if len(checkedDevices) == 0:
            return
        buttonUnlocker = ButtonUnlocker(len(checkedDevices), (self.openButton, self.closeButton, self.captureButton, self.checkAllButton))
        for i in checkedDevices:
            localThread = threading.Thread(target = self.captureThread, args = (i[0], i[1], i[3], buttonUnlocker))
            localThread.start()

    def captureThread(self, device, model, statusLabel, buttonUnlocker):
        removeSSPermission = self.optionsHandler.getOption('Remove SS from device', bool)
        pathToScreenOnDevice = ''
        rawFileName = self.getFileName(device, model)
        indexedFileName = self.getFileNameWithIndex(rawFileName)
        statusLabel.SetLabel('Taking screenshot...')
        clbk = self.adb.captureScreenshot(device, indexedFileName)
        try:
            statusLabel.SetLabel(clbk[0])
        except RuntimeError:
            return
        if not clbk[1]:
            buttonUnlocker.finishThread()
            return
        pathToScreenOnDevice = clbk[1]
        clbk = self.adb.pullScreenshot(device, pathToScreenOnDevice, self.directory)
        try:
            statusLabel.SetLabel(clbk)
            if not removeSSPermission:
                buttonUnlocker.finishThread()
            else:
                time.sleep(1)
                statusLabel.SetLabel('Removing...')
                clbk = self.adb.deleteFile(device, pathToScreenOnDevice)
                statusLabel.SetLabel(clbk)
                buttonUnlocker.finishThread()
        except RuntimeError:
            return

    def getFileNameWithIndex(self, rawFileName):
        currentlyExistingFiles = glob.glob(os.path.join(self.directory, '{}*'.format(rawFileName)))
        if len(currentlyExistingFiles) > 0:
            lastIndex = self.getIndexOfFile(max(currentlyExistingFiles, key = self.getIndexOfFile), nextIndx = True)
            fileName = '{}_{}.png'.format(rawFileName, lastIndex)
            return fileName
        else:
            fileName = '{}_1.png'.format(rawFileName)
            return fileName
    
    def getIndexOfFile(self, f, nextIndx = False):
        curIndex = int(f[f.find('_')+1:f.find('.png')])
        if nextIndx:
            return curIndex+1
        else:
            return curIndex

    def getFileName(self, device, model):
        unsupportedChars = (' ', '(', ')', '_')
        for i in unsupportedChars:
            model = model.replace(i, '')
        deviceScreenSize = self.adb.getDeviceScreenSize(device)
        return '{}-{}'.format(model, deviceScreenSize)

    def openScreenshotsFolder(self, event):
        os.startfile(self.directory)
    
    def switchAllCheckboxes(self, event):
        self.devicesSizer.switchCheckboxes(self.checkboxesState)
        self.checkboxesState = not self.checkboxesState
        event.GetEventObject().SetLabel('Uncheck all' if self.checkboxesState == False else 'Check all')

    def onClose(self, event):
        del self.disabler
        self.mainFrame.Raise()
        self.Destroy()

class BuildInstallerFrame(wx.Frame):
    def __init__(self, mainFrame, adb, optionsHandler):
        wx.Frame.__init__(self, mainFrame, title = 'Installing builds', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.mainFrame = mainFrame
        self.adb = adb
        self.optionsHandler = optionsHandler
        self.checkboxesState = True
        self.buildChosen = ''
        self.disabler = wx.WindowDisabler(self)
        self.panel = wx.Panel(self)

        self.selectBuildButton, self.chooseLatestBuildButton, self.chosenBuildTextCtrl, self.devicesSizer, self.installBuildButton, self.checkAllButton, self.closeButton, self.optionsCombobox = self.createControls()

        self.Bind(wx.EVT_BUTTON, self.selectBuild, self.selectBuildButton)
        self.Bind(wx.EVT_BUTTON, self.getLatestBuildFromOptionsFolder, self.chooseLatestBuildButton)
        self.Bind(wx.EVT_BUTTON, self.installBuild, self.installBuildButton)
        self.Bind(wx.EVT_BUTTON, self.switchAllCheckboxes, self.checkAllButton)
        self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)

        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.Fit()
        self.Show()

    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        #top part of frame

        buildsManageSizer = wx.BoxSizer(wx.VERTICAL)

        buildsButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        selectBuildButton = wx.Button(self.panel, wx.ID_ANY, 'Select build')
        buildsButtonsSizer.Add(selectBuildButton, 1, wx.EXPAND | wx.ALL, 5)
        chooseLatestButton = wx.Button(self.panel, wx.ID_ANY, 'Get latest from default folder')
        buildsButtonsSizer.Add(chooseLatestButton, 1, wx.EXPAND | wx.ALL, 5)

        chosenBuildTextCtrl = wx.TextCtrl(self.panel, value = 'Drag and drop build here', style = wx.TE_READONLY | wx.TE_CENTRE)
        dragAndDropHandler = FileDragAndDropHandler(chosenBuildTextCtrl, self.panel)
        chosenBuildTextCtrl.SetDropTarget(dragAndDropHandler)

        buildsManageSizer.Add(buildsButtonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        buildsManageSizer.Add(chosenBuildTextCtrl, 0, wx.CENTRE | wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(buildsManageSizer, 0, wx.EXPAND | wx.ALL, 5)

        #middle part of frame

        devicesList = self.adb.getListOfAttachedDevices()
        devicesSizer = AuthorizedDevicesSizer(self.panel, devicesList, self.adb)

        mainSizer.Add(devicesSizer, 1, wx.EXPAND | wx.ALL, 5)

        #bottom part of frame

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        installBuildButton = wx.Button(self.panel, wx.ID_ANY, 'Install')
        buttonSizer.Add(installBuildButton, 0, wx.EXPAND | wx.ALL, 3)

        optionCombobox = wx.ComboBox(self.panel, wx.ID_ANY, value = 'Clean', choices = ('Clean', 'Overwrite'), style = wx.CB_READONLY)
        buttonSizer.Add(optionCombobox, 0, wx.EXPAND | wx.ALL, 3)

        checkAllButton = wx.Button(self.panel, wx.ID_ANY, 'Select all')
        buttonSizer.Add(checkAllButton, 0, wx.EXPAND | wx.ALL, 3)

        closeButton = wx.Button(self.panel, wx.ID_ANY, 'Close')
        buttonSizer.Add(closeButton, 0, wx.EXPAND | wx.ALL, 3)

        mainSizer.Add(buttonSizer, 0, wx.CENTER | wx.ALL, 5)

        self.panel.SetSizer(mainSizer)
        self.panel.Fit()

        return selectBuildButton, chooseLatestButton, chosenBuildTextCtrl, devicesSizer, installBuildButton, checkAllButton, closeButton, optionCombobox

    def setBuild(self, build):
        self.buildChosen = build
        self.chosenBuildTextCtrl.SetValue(self.buildChosen)
    
    ### EVENTS ###

    def installBuild(self, event):
        option = self.optionsCombobox.GetValue()
        checkedDevices = self.devicesSizer.getCheckedDevices()
        if len(checkedDevices) == 0:
            return
        if not self.buildChosen.endswith('.apk'):
            errorDlg = wx.MessageDialog(self, "Please choose build!", 'Error!',
                                         style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return
        buttonUnlocker = ButtonUnlocker(len(checkedDevices), (self.selectBuildButton, self.chooseLatestBuildButton, self.installBuildButton, self.checkAllButton, self.closeButton, self.optionsCombobox))
        for i in checkedDevices:
            thread = threading.Thread(target = self.installingThread, args = (i[0], self.buildChosen, i[3], option, buttonUnlocker))
            thread.start()

    def installingThread(self, device, build, statusLabel, option, buttonUnlocker):
        buildPackage = self.adb.getPackageNameOfAppFromApk(build)
        buildVer = self.adb.getBuildVersionFromApk(build)
        if option == 'Clean':
            statusLabel.SetLabel('Checking if exists...'.format(buildPackage))
            statusLabel.Refresh()
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

    def selectBuild(self, event):
        with wx.FileDialog(self, 'Choose build', wildcard = '*.apk', style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:
            if fd.ShowModal() == wx.ID_CANCEL:
                return ''
            else:
                self.setBuild(fd.GetPath())

    def getLatestBuildFromOptionsFolder(self, event):
        buildFolder = self.optionsHandler.getOption('Builds folder', str)
        builds = glob.glob(os.path.join(buildFolder, '*.apk'))
        latestBuild = max(builds, key = os.path.getctime)
        self.setBuild(latestBuild)

    def switchAllCheckboxes(self, event):
        self.devicesSizer.switchCheckboxes(self.checkboxesState)
        self.checkboxesState = not self.checkboxesState
        event.GetEventObject().SetLabel('Uncheck all' if self.checkboxesState == False else 'Check all')
    
    def onClose(self, event):
        del self.disabler
        self.mainFrame.Raise()
        self.Destroy()

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
            if len(self.optionsHandler.getOption('Jenkins credentials', tuple)) != 2:
                errorDlg = wx.MessageDialog(self.parent, 'Please provide your jenkins credentials (file -> options)', 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
                errorDlg.ShowModal()
                return
            buildInfo = RetrieveLinkDialog(self.parent, info, self.optionsHandler).getLink()
            DownloadBuildDialog(self.parent, buildInfo, self.optionsHandler).downloadBuild()
        return getBuildEvent

class AuthorizedDevicesSizer(wx.BoxSizer):
    def __init__(self, parentPanel, devicesList, adb):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.parentPanel = parentPanel
        self.adb = adb
        self.devicesList = self.getAuthorizedDevices(devicesList)
        '''
        self.lst is a list of tuples
        each tuple contain 4 elements:
        [0] - device id (used in adb methods call)
        [1] - device model (retrieved by adb method)
        [2] - checkbox object reference - to get info whether checkbox is ticked or not
        [3] - status control - used in screenshot capture flow that sets status according to callback from adb method
        '''
        self.lst = self.createControls()

    def createControls(self):
        localLst = []

        modelColumn = wx.BoxSizer(wx.VERTICAL)
        checkboxColumn = wx.BoxSizer(wx.VERTICAL)
        statusColumn = wx.BoxSizer(wx.VERTICAL)

        columnHeaderFont = wx.Font(14, wx.MODERN, wx.ITALIC, wx.LIGHT)

        modelColumnHeader = wx.StaticText(self.parentPanel, label = 'Device', style = wx.CENTER)
        modelColumnHeader.SetFont(columnHeaderFont)
        modelColumn.Add(modelColumnHeader, 0, wx.CENTER | wx.ALL, 3)

        checkboxColumnHeader = wx.StaticText(self.parentPanel, label = 'Check', style = wx.CENTER)
        checkboxColumnHeader.SetFont(columnHeaderFont)
        checkboxColumn.Add(checkboxColumnHeader, 0, wx.CENTER | wx.ALL, 3)

        statusColumnHeader = wx.StaticText(self.parentPanel, label = 'Status', style = wx.CENTER)
        statusColumnHeader.SetFont(columnHeaderFont)
        statusColumn.Add(statusColumnHeader, 0, wx.CENTER | wx.ALL, 3)

        for i in self.devicesList:
            model = self.adb.getDeviceModel(i)

            deviceLabel = wx.StaticText(self.parentPanel, label = model, style = wx.CENTER)
            modelColumn.Add(wx.StaticLine(self.parentPanel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            modelColumn.Add(deviceLabel, 0, wx.CENTER | wx.ALL, 10)

            checkbox = wx.CheckBox(self.parentPanel, style = wx.CENTER)
            checkboxColumn.Add(wx.StaticLine(self.parentPanel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            checkboxColumn.Add(checkbox, 0, wx.CENTER | wx.ALL, 10)

            statusLabel = wx.StaticText(self.parentPanel, label = 'Ready')
            statusColumn.Add(wx.StaticLine(self.parentPanel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            statusColumn.Add(statusLabel, 0, wx.CENTER | wx.EXPAND | wx.ALL, 10)

            localLst.append((i, model, checkbox, statusLabel))

        self.Add(modelColumn, 3, wx.EXPAND | wx.CENTER | wx.ALL, 5)
        self.Add(wx.StaticLine(self.parentPanel, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5)
        self.Add(checkboxColumn, 1, wx.EXPAND | wx.CENTER | wx.ALL, 5)
        self.Add(wx.StaticLine(self.parentPanel, size = (2, 2), style = wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5)
        self.Add(statusColumn, 3, wx.EXPAND | wx.CENTER | wx.ALL, 5)

        return localLst
    
    def getAuthorizedDevices(self, rawList):
        activeList = []
        for i in rawList:
            if i[1] == 'device':
                activeList.append(i[0])
        return activeList

    def getCheckedDevices(self):
        checkedDevices = []
        for i in self.lst:
            if i[2].GetValue() == True:
                checkedDevices.append(i)
        return checkedDevices

    def switchCheckboxes(self, state):
        for i in self.lst:
            i[2].SetValue(state)

class RetrieveLinkDialog(wx.GenericProgressDialog):
    def __init__(self, parent, info, optionsHandler):
        wx.GenericProgressDialog.__init__(self, 'Working...', 'Retrieving build information...', style = wx.PD_APP_MODAL)
        self.parent = parent
        self.optionsHandler = optionsHandler
        self.info = info
        self.auth = self.optionsHandler.getOption('Jenkins credentials', tuple)

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
        buildFolder = self.optionsHandler.getOption('Builds folder', str)
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

class ButtonUnlocker():
    def __init__(self, count, btns):
        self.count = count
        self.semph = threading.Semaphore()
        self.buttons = btns
        for i in self.buttons:
            i.Disable()

    def finishThread(self):
        self.semph.acquire()
        try:
            self.count -= 1
            if self.count == 0:
                for i in self.buttons:
                    i.Enable()
        finally:
            self.semph.release()

class OptionsHandler():
    def __init__(self):
        self.optionsPath = os.path.join(os.getenv('APPDATA'), 'adbgui')
        self.optionsFilePath = os.path.join(self.optionsPath, 'options.json')
        self.optionsCats = ('Screenshots folder', 'Builds folder', 'Jenkins credentials', 'Remove SS from device')
        self.optionsTypes = ('folder', 'folder', 'input', 'checkbox')
        self.__optionsCategories = [(i, j) for i, j in zip(self.optionsCats, self.optionsTypes)]
        self.__options = self.getOptionsIfAlreadyExist()

    def getOptionsIfAlreadyExist(self):
        if os.path.exists(self.optionsPath):
            try:
                with open(self.optionsFilePath, 'r') as f:
                    try:
                        return json.loads(f.read())
                    except json.decoder.JSONDecodeError:
                        return {}
            except FileNotFoundError:
                return {}
        else:
            os.mkdir(self.optionsPath)
            return {}

    def setOption(self, option, value):
        self.__options[option] = value

    def getOption(self, option, type):
        if option not in self.optionsCats:
            assert(False)
            sys.exit(1)
        try:
            return self.__options[option]
        except KeyError:
            if type == tuple:
                return ('', '')
            elif type == str:
                return ''
            elif type == bool:
                return False
            else:
                assert(False)

    def saveOptionsToFile(self):
        with open(self.optionsFilePath, 'w+') as f:
            json.dump(self.__options, f)

    def getOptionsCategories(self):
        return self.__optionsCategories

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
    def deleteFile(device, fullPath):
        try:
            subprocess.check_output(r'adb -s {} shell rm {}'.format(device, fullPath))
            return 'Done deleting'
        except subprocess.CalledProcessError:
            return 'Error!'

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
        brand = subprocess.check_output(r'adb -s {} shell getprop ro.product.brand'.format(device), shell = True)
        if len(brand) > 0:
            return brand
        else:
            return 'N/A'

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

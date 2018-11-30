import glob
import os
import time
import threading
import wx

import authorizeddevicessizer
import buttonunlocker
import filedraganddrophandler

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
        dragAndDropHandler = filedraganddrophandler.FileDragAndDropHandler(chosenBuildTextCtrl, self.panel)
        chosenBuildTextCtrl.SetDropTarget(dragAndDropHandler)

        buildsManageSizer.Add(buildsButtonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        buildsManageSizer.Add(chosenBuildTextCtrl, 0, wx.CENTRE | wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(buildsManageSizer, 0, wx.EXPAND | wx.ALL, 5)

        #middle part of frame

        devicesList = self.adb.getListOfAttachedDevices()
        devicesSizer = authorizeddevicessizer.AuthorizedDevicesSizer(self.panel, devicesList, self.adb)

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
        buttonUnlocker = buttonunlocker.ButtonUnlocker(len(checkedDevices), (self.selectBuildButton, self.chooseLatestBuildButton, self.installBuildButton, self.checkAllButton, self.closeButton, self.optionsCombobox))
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

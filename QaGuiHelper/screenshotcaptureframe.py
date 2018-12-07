import glob
import os
import threading
import time
import wx

from authorizeddevicessizer import AuthorizedDevicesSizer
from buttonunlocker import ButtonUnlocker

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
        try:
            statusLabel.SetLabel('Taking screenshot...')
            status, msg, dirOnDevice = self.adb.captureScreenshot(device, indexedFileName)
            statusLabel.SetLabel(msg)
            if status == False:
                buttonUnlocker.finishThread()
                return
            time.sleep(1)
            statusLabel.SetLabel('Pulling screenshot')
            time.sleep(1)
            status, msg = self.adb.pullScreenshot(device, dirOnDevice, self.directory)
            statusLabel.SetLabel(msg)
            if status == False:
                buttonUnlocker.finishThread()
                return
            else:
                if not removeSSPermission:
                    buttonUnlocker.finishThread()
                    return
                else:
                    time.sleep(1)
                    statusLabel.SetLabel('Removing...')
                    _, msg = self.adb.deleteFile(device, pathToScreenOnDevice)
                    statusLabel.SetLabel(msg)
                    buttonUnlocker.finishThread()
                    return
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
        status, deviceScreenSize = self.adb.getDeviceScreenSize(device)
        if status == False:
            return 'unknown'
        else:
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

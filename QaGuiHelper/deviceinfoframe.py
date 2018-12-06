import threading
import wx

from InstalledPackagesListFrame import InstalledPackagesListFrame

class DeviceInfoFrame(wx.Frame):
    def __init__(self, parentFrame, deviceId, adb):
        wx.Frame.__init__(self, parentFrame, title = 'Device Info', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.parentFrame = parentFrame
        self.deviceId = deviceId
        self.adb = adb
        self.disabler = wx.WindowDisabler(self)
        self.deviceInfoTable = (
            ('Brand', self.adb.getProperty, 'field', 'ro.product.brand'),
            ('Model', self.adb.getProperty, 'field', 'ro.product.model'),
            ('Screen size', self.adb.getDeviceScreenSize, 'field'),
            ('IP Address', self.adb.getDeviceIpAddress, 'field'),
            ('ADB tcpip port', self.adb.getProperty, 'field', 'service.adb.tcp.port'),
            ('Battery', self.adb.getBatteryStatus, 'field'),
            ('Plugged in?', self.adb.getPluggedInStatus, 'field'),
            ('OS version', self.adb.getProperty, 'field', 'ro.build.version.release'),
            ('API version', self.adb.getProperty, 'field', 'ro.build.version.sdk'),
            ('Device timezone', self.adb.getProperty, 'field', 'persist.sys.timezone'),
            ('Device language', self.adb.getProperty, 'field', 'persist.sys.locale'),
            ('Marketing name', self.adb.getProperty, 'field', 'ro.config.marketing_name'),
            ('Wifi name', self.adb.getWifiName, 'field'),
            ('Serial No', self.adb.getProperty, 'field', 'ro.boot.serialno'),
            ('Installed packages', self.adb.getListOfInstalledPackages, 'button'))
        self.installedPackagesList = None
        self.panel = wx.Panel(self)
        self.deviceInfoControls, self.showPackagesButton, self.closeBtn, = self.createControls()
        self.updateFields()

        self.Bind(wx.EVT_BUTTON, self.showPackages, self.showPackagesButton)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onClose, self.closeBtn)
        self.Fit()
        self.Show(True)

    def createControls(self):
        deviceInfoControls = []
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        for idx, i in enumerate(self.deviceInfoTable):
            if idx > 0:
                mainSizer.Add(wx.StaticLine(self.panel, size = (2, 2), style = wx.LI_HORIZONTAL), 0, wx.EXPAND)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self.panel, label = i[0], size = (100, -1), style = wx.TE_CENTRE)
            sizer.Add(label, 0, wx.EXPAND | wx.TOP, label.GetSize()[1]/3.5)
            if i[2] == 'field':
                content = wx.TextCtrl(self.panel, value = '...', size = (150, -1), style = wx.TE_READONLY)
                deviceInfoControls.append(content)
                sizer.Add(content, 0, wx.ALIGN_RIGHT)
            elif i[2] == 'button':
                btn = wx.Button(self.panel, wx.ID_ANY, 'Show')
                deviceInfoControls.append(btn)
                sizer.Add(btn, 0, wx.LEFT, 20)
            mainSizer.Add(sizer, 0, wx.ALL, 5)
    
        closeBtn = wx.Button(self.panel, wx.ID_ANY, 'Close')
        mainSizer.Add(closeBtn, 0, wx.CENTRE | wx.ALL, 5)

        self.panel.SetSizer(mainSizer)
        self.panel.Fit()

        return deviceInfoControls, btn, closeBtn

    def updateFields(self):
        for functionInfo, target in zip(self.deviceInfoTable, self.deviceInfoControls):
            if len(functionInfo) > 3:
                args = (target, functionInfo[1], functionInfo[3])
            else:
                args = (target, functionInfo[1])    
            localThread = threading.Thread(target = self.updateSingleControl, args = args)
            localThread.start()

    def updateSingleControl(self, target, functionToCall, propertyArg = None):
        localArgs = None
        if propertyArg == None:
            localArgs = (self.deviceId, )
        else:
            localArgs = (self.deviceId, propertyArg)
        status, msg = functionToCall(*localArgs)
        if type(target) == wx.TextCtrl:
            try:
                target.SetValue(msg)
            except RuntimeError:
                pass
        elif type(target) == wx.Button:
            try:
                target.Disable()
                target.info = status, msg
                target.Enable()
            except RuntimeError:
                pass
        else:
            assert(False)

    ### EVENTS ###

    def showPackages(self, event):
        status, message = event.GetEventObject().info
        if status == False:
            errorDlg = wx.MessageDialog(self, message, 'Error!',
                                        style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            return        
        InstalledPackagesListFrame(self, self.deviceId, self.adb, message)

    def onClose(self, event):
        del self.disabler
        self.parentFrame.Raise()
        self.Destroy()
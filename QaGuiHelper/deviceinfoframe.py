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
            ('Brand', self.adb.getBrand, 'field'),
            ('Model', self.adb.getDeviceModel, 'field'),
            ('Screen size', self.adb.getDeviceScreenSize, 'field'),
            ('IP Address', self.adb.getDeviceIpAddress, 'field'),
            ('ADB tcpip port', self.adb.getTcpipPort, 'field'),
            ('Battery', self.adb.getBatteryStatus, 'field'),
            ('Plugged in?', self.adb.getPluggedInStatus, 'field'),
            ('OS version', self.adb.getOsVersion, 'field'),
            ('API version', self.adb.getApiVersion, 'field'),
            ('Device timezone', self.adb.getDeviceTimezone, 'field'),
            ('Device language', self.adb.getDeviceLanguage, 'field'),
            ('Marketing name', self.adb.getMarketingName, 'field'),
            ('Wifi name', self.adb.getWifiName, 'field'),
            ('Serial No', self.adb.getSerialNo, 'field'),
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
                sizer.Add(btn, 0, wx.ALIGN_RIGHT)
            mainSizer.Add(sizer, 0, wx.ALL, 5)
    
        closeBtn = wx.Button(self.panel, wx.ID_ANY, 'Close')
        mainSizer.Add(closeBtn, 0, wx.CENTRE | wx.ALL, 5)

        self.panel.SetSizer(mainSizer)
        self.panel.Fit()

        return deviceInfoControls, btn, closeBtn

    def updateFields(self):
        for func, target in zip(self.deviceInfoTable, self.deviceInfoControls):
            localThread = threading.Thread(target = self.updateSingleControl, args = (target, func[1]))
            localThread.start()

    def updateSingleControl(self, target, functionToCall):
        if type(target) == wx.TextCtrl:            
            try:
                target.SetValue(functionToCall(self.deviceId))
            except RuntimeError:
                pass
        elif type(target) == wx.Button:
            target.Disable()
            target.info = functionToCall(self.deviceId)
            target.Enable()
        else:
            assert(False)

    ### EVENTS ###

    def showPackages(self, event):
        InstalledPackagesListFrame(self, self.deviceId, self.adb, event.GetEventObject().info)

    def onClose(self, event):
        del self.disabler
        self.parentFrame.Raise()
        self.Destroy()
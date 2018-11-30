import threading
import wx

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

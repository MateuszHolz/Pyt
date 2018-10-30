import json
import os
import re
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
        self.console = Console(self)
        self.devicesPanel = DevicesPanel(self, self.console, self.adb)

        mainSizer.Add(self.devicesPanel, 1)
        mainSizer.Add(self.console, 1)

        fileMenu = wx.Menu()
        options = fileMenu.Append(wx.ID_ANY, 'Options')
        fileMenu.AppendSeparator()
        ext = fileMenu.Append(wx.ID_ANY, 'Exit')

        jenkinsMenu = wx.Menu()

        links = {}
        with open('links.json', 'r') as f:
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
                            self.Bind(wx.EVT_MENU, self.getBuild(links[platforms][projects][environment][buildVersion][branchOption]), menuItem)
                        environmentMenu.Append(wx.ID_ANY, buildVersion, buildVersionMenu)
                    projectMenu.Append(wx.ID_ANY, environment, environmentMenu)
                platformMenu.Append(wx.ID_ANY, projects, projectMenu)
            jenkinsMenu.Append(wx.ID_ANY, platforms, platformMenu)
            
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

    def getBuild(self, buildLink):
        def getBuildEvent(event):
            print('Event download build: {}'.format(buildLink))
        return getBuildEvent

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

class Console(wx.TextCtrl):
    def __init__(self, parent):
        self.console = wx.TextCtrl.__init__(self, parent, style = wx.TE_MULTILINE | wx.TE_READONLY, size = (300, 400))
        self.curLines = 0

    def clear(self):
        self.SetValue('')

    def addText(self, text):
        self.AppendText(text+'\n')

class InProgressFrame(wx.Frame):
    def __init__(self, parent, disabler, console):
        self.frame = wx.Frame.__init__(self, parent, title = 'inprogressframe')
        self.disabler = disabler
        self.parent = parent

        self.labelSizer = wx.BoxSizer(wx.VERTICAL)
        self.labels = []
        for i in range(0, 5):
            self.labels.append(wx.TextCtrl(self, style = wx.ALIGN_CENTRE_HORIZONTAL | wx.TE_READONLY))
            self.labelSizer.Add(self.labels[i], 1, wx.EXPAND)
        self.newBtn1 = wx.Button(self, -1, 'ddddd')
        self.labelSizer.Add(self.newBtn1, 1, wx.EXPAND)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.newBtn1)
        self.stopWorking = False
    
    def show(self):
        self.SetSizer(self.labelSizer)
        self.SetAutoLayout(1)
        self.labelSizer.Fit(self)
        self.Show(True)

    def OnButton(self, event):
        self.t = threading.Thread(target = self.worker, args = (self, ))
        self.t.start()
    
    def worker(self, frame):
        for i in range(0, 1000):
            if frame.stopWorking:
                print('stop working')
                return
            self.labels[1].SetValue(str(i))
            time.sleep(0.01)

    def OnClose(self, event):
        self.stopWorking = True
        self.Destroy()
        self.parent.Raise() ## without that, parent frame hides behind opened windows (for example google chrome)

class DevicesPanel(wx.Panel):
    def __init__(self, parent, console, adb):
        self.panel = wx.Panel.__init__(self, parent, size = (5, 400))
        self.parent = parent
        self.adb = adb
        self.console = console
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent, self.adb)
        self.buttonsPanel = RefreshButtonPanel(self)

        self.sizer.Add(self.buttonsPanel, 1, wx.EXPAND)
        self.sizer.Add(self.checkBoxesPanel, 10, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.Fit()
    
    def refreshCheckboxesPanel(self):
        self.sizer.Remove(1)
        self.checkBoxesPanel.Destroy()
        self.checkBoxesPanel = DevicesCheckboxesPanel(self, self.parent, self.adb)
        self.sizer.Add(self.checkBoxesPanel, 10, wx.EXPAND)
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
        self.activeDeviceList = self.adb.getListOfAttachedDevices()
        self.checkBoxesCtrls = []
        self.createPanel()

    def createPanel(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        id = 0
        for i in self.activeDeviceList:
            recordSizer = wx.BoxSizer(wx.HORIZONTAL)

            checkBx = wx.CheckBox(self, -1, label = self.adb.getDeviceModel(i), size = (100, 20), style = wx.ALIGN_RIGHT)
            self.checkBoxesCtrls.append(checkBx)
            recordSizer.Add(checkBx, 0, wx.ALIGN_CENTER)

            infoButton = wx.Button(self, label = 'i', size = (20, 20))
            self.Bind(wx.EVT_BUTTON, self.OnInfoButton(id), infoButton)
            recordSizer.Add(infoButton, 0, wx.ALIGN_CENTER)

            mainSizer.Add(recordSizer, 0, wx.ALIGN_CENTER)
            id += 1
        self.SetSizer(mainSizer)
        mainSizer.Layout()
        self.Fit()

    def getCheckedDevices(self):
        checkedRecords = []
        for i, j in zip(self.checkBoxesCtrls, self.activeDeviceList):
            if i.GetValue() == True:
                checkedRecords.append(j)
        return checkedRecords
    
    def OnInfoButton(self, id):
        def OnClick(event):
            disabler = wx.WindowDisabler()
            DeviceInfoWindow(self, self.mainWindow, self.activeDeviceList[id], disabler, self.adb)
        return OnClick

class RefreshButtonPanel(wx.Panel):
    def __init__(self, parent):
        self.panel = wx.Panel.__init__(self, parent)
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.createPanel()

    def createPanel(self):
        topRow = wx.BoxSizer(wx.HORIZONTAL)
        captureSSBtn = wx.Button(self, wx.ID_ANY, 'Capture SS')
        installBuildBtn = wx.Button(self, wx.ID_ANY, 'Install Build')
        topRow.Add(captureSSBtn, 0, wx.ALIGN_CENTER)
        topRow.Add(installBuildBtn, 0, wx.ALIGN_CENTER)

        bottomRow = wx.BoxSizer(wx.HORIZONTAL)
        refreshDevicesBtn = wx.Button(self, wx.ID_ANY, 'Refresh')
        bottomRow.Add(refreshDevicesBtn, 0, wx.ALIGN_CENTER)
        placeholderBtn = wx.Button(self, wx.ID_ANY, 'Placeholder')
        bottomRow.Add(placeholderBtn, 0, wx.ALIGN_CENTER)

        self.sizer.Add(topRow, 0, wx.ALIGN_CENTER)
        self.sizer.Add(bottomRow, 0, wx.ALIGN_CENTER)

        self.Bind(wx.EVT_BUTTON, self.getScreenshotFromDevices, captureSSBtn)
        self.Bind(wx.EVT_BUTTON, self.getAndInstallBuild, installBuildBtn)
        self.Bind(wx.EVT_BUTTON, self.refreshDevicesPanel, refreshDevicesBtn)
        self.Bind(wx.EVT_BUTTON, self.getStateOfCheckboxes, placeholderBtn)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

    def getScreenshotFromDevices(self, event):
        raise Exception('not implemented yet')

    def refreshDevicesPanel(self, event):
        self.parent.refreshCheckboxesPanel()

    def getStateOfCheckboxes(self, event):
        print(self.parent.checkBoxesPanel.getCheckedDevices())
    
    def getAndInstallBuild(self, event):
        print('getAndInstallBuild')

    def placeholderMethod(self, event):
        print('placeholderMethod')

class DeviceInfoWindow(wx.Frame):
    def __init__(self, parent, mainWindow, deviceId, disabler, adb):
        self.window = wx.Frame.__init__(self, parent, title = 'Device Info')
        self.parent = parent
        self.mainWindow = mainWindow
        self.deviceId = deviceId
        self.disabler = disabler
        self.deviceInfoControls = []
        self.adb = Adb()
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
            ('Wifi name', self.adb.getWifiName))
        self.createControls()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Show(True)
        self.updateFields()
    
    def createControls(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        for i in self.deviceInfoTable:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label = i[0], size = (100, -1), style = wx.TE_CENTRE)
            sizer.Add(label, 0, wx.EXPAND)
            content = wx.TextCtrl(self, value = '...', size = (150, -1), style = wx.TE_READONLY)
            self.deviceInfoControls.append(content)
            sizer.Add(content, 0, wx.ALIGN_RIGHT)
            mainSizer.Add(sizer, 0)
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

    def OnClose(self, event):
        self.Destroy()
        self.mainWindow.Raise() ## without that, parent frame hides behind opened windows (for example google chrome)

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
                devices.append(tempList[i].decode())
        return devices

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
        return subprocess.check_output(r'adb -s {} shell getprop ro.product.model'.format(device), shell = True)

    @staticmethod
    def getDeviceTimezone(device):
        return subprocess.check_output(r'adb -s {} shell getprop persist.sys.timezone'.format(device), shell = True)

    @staticmethod
    def getDeviceLanguage(device):
        return subprocess.check_output(r'adb -s {} shell getprop persist.sys.locale'.format(device), shell = True)

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
    
if __name__ == '__main__':
    app = wx.App(False)
    MainFrame(None, 'ADB GUI')
    app.MainLoop()

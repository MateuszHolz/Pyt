import wx

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

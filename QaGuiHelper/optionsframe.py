import wx

from JenkinsCredentialsEditFrame import JenkinsCredentialsEditFrame

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

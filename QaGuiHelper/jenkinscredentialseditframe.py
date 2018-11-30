import wx

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

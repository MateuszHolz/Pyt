import json
import wx

import downloadbuilddialog
import retrievelinkdialog

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
            buildInfo = retrievelinkdialog.RetrieveLinkDialog(self.parent, info, self.optionsHandler).getLink()
            downloadbuilddialog.DownloadBuildDialog(self.parent, buildInfo, self.optionsHandler).downloadBuild()
        return getBuildEvent

import requests
import wx

class RetrieveLinkDialog(wx.GenericProgressDialog):
    def __init__(self, parent, info, optionsHandler):
        wx.GenericProgressDialog.__init__(self, 'Working...', 'Retrieving build information...', style = wx.PD_APP_MODAL)
        self.parent = parent
        self.optionsHandler = optionsHandler
        self.info = info
        self.auth = self.optionsHandler.getOption('Jenkins credentials', tuple)

    def getLink(self):
        if self.info[1] == '':
            link = self.getDirectLinkToBuild(self.info[0], self.info[2]), self.auth
        else:
            link = self.getDirectLinkToBuild(self.getLinkToLatestBranch(self.info[0], self.info[1]), self.info[2]), self.auth
        self.Close()
        return link

    def getLinkToLatestBranch(self, jobLink, branchName):
        self.Pulse()
        linkContent = self.requestSiteContent(jobLink)
        curBuildName = self.getBuildName(linkContent, '')
        if branchName in curBuildName:
            return jobLink
        else:
            self.Pulse()
            lastCheckedVersionCode = self.getVersionCode(jobLink)
            newLink = '{}{}'.format(jobLink[:jobLink.find('lastSuccessfulBuild')], int(lastCheckedVersionCode)-1)
            while True:
                self.Pulse()
                newSiteContent = self.requestSiteContent(newLink)
                self.Pulse()
                newBuildName = self.getBuildName(newSiteContent, '')
                if branchName in newBuildName:
                    return newLink
                else:
                    lastCheckedVersionCode = self.getVersionCode(newLink)
                    newLink = '{}{}/'.format(newLink[:newLink.find(lastCheckedVersionCode)], int(lastCheckedVersionCode)-1)
    
    def getVersionCode(self, link):
        siteContent = self.requestSiteContent(link)
        version = siteContent.text.find('Build #')
        version = siteContent.text[version:version+40].split()
        return version[1][1:]

    def getDirectLinkToBuild(self, jobLink, buildVer):
        linkContent = self.requestSiteContent(jobLink)
        buildName = self.getBuildName(linkContent, buildVer)
        buildSize = self.getBuildSize(linkContent, buildName)
        directLink = '{}{}{}'.format(jobLink, '/artifact/output/', buildName)
        return directLink, buildName, buildSize

    def getBuildName(self, siteContent, buildVer):
        for i in siteContent.text.split():
            if "HuuugeStars" in i and buildVer in i and not 'dSYM.zip' in i:
                id1 = i.find("HuuugeStars")
                if i.find(".apk") > 0:
                    id2 = i.find(".apk")+4
                else:
                    id2 = i.find(".ipa")+4
                return i.rstrip()[id1:id2]
        return ''

    def getBuildSize(self, siteContent, buildName):
        localId = siteContent.text.find(buildName)
        cont = siteContent.text[localId:localId+300].split()
        for i in cont:
            if 'fileSize' in i:
                return i[i.find('>')+1:]

    def requestSiteContent(self, link):
        response = requests.get(link, auth = (self.auth[0], self.auth[1]))
        if response.ok:
            return response
        else:
            errorDlg = wx.MessageDialog(self.parent, 'Incorrect response from jenkins! Error code: {}.'.format(response.status_code), 'Error!', style = wx.CENTRE | wx.STAY_ON_TOP | wx.ICON_ERROR)
            errorDlg.ShowModal()
            self.Destroy()
            return

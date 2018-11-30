import os
import requests
import wx

class DownloadBuildDialog(wx.GenericProgressDialog):
    def __init__(self, parent, info, optionsHandler):
        self.parent = parent
        self.info = info
        self.optionsHandler = optionsHandler
        self.dlg = wx.GenericProgressDialog.__init__(self, 'Downloading build!', self.info[0][1])

    def downloadBuild(self):
        buildFolder = self.optionsHandler.getOption('Builds folder', str)
        response = requests.get(self.info[0][0], auth = (self.info[1][0], self.info[1][1]), stream = True)
        with open(os.path.join(buildFolder, self.info[0][1]), 'wb') as f:
            buildSize = float(self.info[0][2]) * 1048576 
            progress = 0
            updateCount = 0
            for b in response.iter_content(chunk_size = 4096):
                progress += len(b)
                updateCount += 1
                f.write(b)
                curProgress = int((progress / buildSize)* 100)
                if updateCount % 50 == 0:
                    progressInMb = str(float(self.info[0][2]) * (curProgress / 100))
                    self.Update(curProgress, '{} \n {}MB / {}MB'.format(self.info[0][1], progressInMb[:progressInMb.find('.')+3], self.info[0][2]))

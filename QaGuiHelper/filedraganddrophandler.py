import wx

class FileDragAndDropHandler(wx.FileDropTarget):
    def __init__(self, parentPanel):
        wx.FileDropTarget.__init__(self)
        self.parentPanel = parentPanel

    def OnDropFiles(self, x, y, filenames):
        extension = '.apk'
        if len(filenames) > 1:
            self.parentPanel.setBuild('Only 1 build at a time allowed.', False)
        else:
            if filenames[0].endswith(extension):
                self.parentPanel.setBuild(filenames[0])
            else:
                self.parentPanel.setBuild('File must end with .apk!', False)
        return True

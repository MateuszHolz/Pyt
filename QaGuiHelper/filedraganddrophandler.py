import wx

class FileDragAndDropHandler(wx.FileDropTarget):
    def __init__(self, target, parentPanel):
        wx.FileDropTarget.__init__(self)
        self.target = target
        self.parentPanel = parentPanel

    def OnDropFiles(self, x, y, filenames):
        extension = '.apk'
        if len(filenames) > 1:
            self.parentPanel.setBuild('', self.target)
            self.target.SetValue('Only 1 file at time is allowed!')
        else:
            if filenames[0].endswith(extension):
                self.parentPanel.setBuild(filenames[0], self.target)
            else:
                self.parentPanel.setBuild('', self.target)
                self.target.SetValue('Dropped file must end with {}'.format(extension))
        return True

from TkTools import *
from BookmarksManager import *
from TScript import *
from ConnectionFrame import *

class CmdWidgetBaseFrame(ttk.Frame):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

        if "section" in kwargs.keys():
            self.__dict__.update(kwargs["section"])

        ttk.Frame.__init__(self, self.parent)

        connectionTitles = self.rootFrame.getListOfTabTitles()
        self.currentConnection = StringVar()
        self.currentConnection.set("-")

        self.connectionsMenu = OptionMenu(self, self.currentConnection, "-")
        self.connectionsMenu.pack(side=TOP, fill=X)
        self.bind("<Visibility>", self.onVisible)
    
    def getCommandResult(self, line):
        cmdResult = None

        try:
            instruction = TScriptCommandParser.build(line)
            cmdResult = instruction.exec(self.env)
        except Exception as e:
            cmdResult = ["{0}\n".format(str(e))]
        
        return cmdResult

    def onConnectionChanged(self, index, title):
        self.env = self.rootFrame.connectionFrames[index].env
        self.currentConnection.set(title)

    def updateAvailableConnections(self):
        titles = self.rootFrame.getListOfTabTitles()

        menu = self.connectionsMenu["menu"]
        menu.delete(0, "end")

        for (i, title) in enumerate(titles):
            newTitle = "[{0}] {1}".format(i, title)
            onSelectCmd = lambda index=i, ttl=newTitle: self.onConnectionChanged(index, ttl)

            menu.add_command(label=newTitle, command=onSelectCmd)

    def onVisible(self, event):
        currentConnectionFrame = self.rootFrame.getCurrentConnectionFrame()
        self.currentConnection.set(currentConnectionFrame.getTitle())
        self.env = currentConnectionFrame.env
        self.updateAvailableConnections()

    def isEntryEditable(self, key):
        return getattr(self, "{0}Editable".format(key), "") == "1"

    def getEntryDescription(self, key):
        return getattr(self, "{0}Description".format(key), "")

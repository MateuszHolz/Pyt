#!/usr/bin/python3

import re
import os

from collections import OrderedDict

from tkinter import *
from tkinter import ttk

from TelnetGuiConfig import *
from ConnectionFrame import *
from BookmarksFrame import *
from TScriptFrame import *
from TkTools import *
from TScript import *
from Version import *
from CmdWidgetsFrame import *

class TelnetGui(ttk.Frame):
    autoexecPath = "{0}/autoexec".format(TScriptFrame.scriptsDirectory)

    maxNumberOfConnections = 5
    configPanelEntries = None
    telnetConnection = None

    config = None
    connectionFrames = []

    # (key, (defaultValue, description))
    defaultGlobalSettings = OrderedDict([
        ("defaultLabel",                ("[$HOST:$PORT]",                    "Default Label")),
        ("defaultHost",                 ("127.0.0.1",                        "Default Host")),
        ("defaultPort",                 ("1337",                             "Default Port")),
        ("defaultPreConnectCommand",    ("adb forward tcp:1337 tcp:1337",    "Default pre-connect command")),
        ("timeStampDateFormat",         ("[%d.%m.%y %H:%M:%S]",              "Timestamp date format")),
        ("editor",                      (r'%windir%\system32\notepad.exe',   "File editor.")),
    ])

    def initMainPanelLayout(self, parent):# {{{
        mainPanel = ttk.Frame(parent)

        self.connectionFrames = []
        self.connectionNotebook = ttk.Notebook(mainPanel)
        self.connectionNotebook.bind("<<NotebookTabChanged>>", lambda event: self.onConnectionTabChanged(event))
        self.connectionNotebook.pack(fill=BOTH, expand=True)

        return mainPanel# }}}

    def initConfigPanelLayout(self, parent):# {{{
        configPanel = ttk.Frame(parent)
        configPanel.pack(side=TOP)

        panel = ttk.Panedwindow(configPanel)
        panel.pack(side=TOP, fill=X)

        # Append global section entries:
        self.configPanelEntries = []
        for key, (defaultValue, description) in self.defaultGlobalSettings.items():
            self.configPanelEntries.append(buildOptionLabel(panel, key, description))
        self.configPanelEntries = OrderedDict(self.configPanelEntries)

        # Append entries for command patterns:
        commandPatterns = self.config.getListOfCommandPatterns()
        for i, pattern in enumerate(commandPatterns):
            label = self.config.cmdPatternFormat.format(i)
            description = "Command regex pattern {0}".format(i)
            (key, entry) = buildOptionLabel(panel, label, description)
            self.configPanelEntries[key] = entry

        for key, (labelFrame, entry) in self.configPanelEntries.items():
            panel.add(labelFrame)
        
        checkboxesFrame = ttk.Frame(configPanel)

        # Rest of boolean options:
        for key, (checkboxDescription, checkboxVariable, defaultValue) in self.boolOptions.items():
            checkboxVariable.set(defaultValue)
            button = Checkbutton(checkboxesFrame, text=checkboxDescription, variable=checkboxVariable, onvalue=1, offvalue=0)
            button.pack(side=LEFT)

        checkboxesFrame.pack(side=TOP)

        bookmarkButton = Button(configPanel, text=("Save to '{0}'".format(self.config.filePath)), command=self.onSaveButtonPressed)
        bookmarkButton.pack(side=TOP, fill=X)

        return configPanel# }}}

    def __init__(self, parent):
        self.parent = parent
        ttk.Frame.__init__(self, parent)
        SyntaxHighlightings.setRootFrame(self)

        self.enabledCmdSort = IntVar()
        self.enabledSyntaxHighlight = IntVar()

        # (key, (defaultValue, description, variable))
        self.boolOptions = OrderedDict([
            ("sortCommands",    ("Sort received list of commands",   self.enabledCmdSort,            0)),
            ("syntaxHighlight", ("Syntax highlighting enabled",      self.enabledSyntaxHighlight,    1)),
        ])

        self.config = TelnetGuiConfig(self)
        self.config.build()

        self.parent = parent
        self.parent.title("TelnetGuiClient v{0}".format(GetVersion()))

        notebook = ttk.Notebook(self.parent)

        tabDefs = [
            ("mainPanel",       "Console",      self.initMainPanelLayout(notebook)),
            ("bookmarksPanel",  "Bookmarks",    BookmarksFrame(notebook)),
            ("scriptPanel",     "Scripts",      TScriptFrame(notebook, self)),
            ("cmdWidgetsPanel", "CmdWidgets",   CmdWidgetsFrame(parent=notebook, rootFrame=self, cmdWidgetSections=self.config.getCmdWidgetSections())),
            ("configPanel",     "Options",      self.initConfigPanelLayout(notebook)),
        ]

        self.tabs = []
        for (fieldName, tabDescription, tabObject) in tabDefs:
            setattr(self, fieldName, tabObject)
            notebook.add(getattr(self, fieldName), text=tabDescription)
            self.tabs.append(tabObject)

        notebook.pack(fill=BOTH, expand=True)

        self.updateConfigPanel()
        self.applyConfig()
        self.readAutoexec()

    def readAutoexec(self):
        currentConnectionFrame = self.connectionFrames[self.getCurrentConnectionIndex()]

        try:
            self.globalScope = TScriptScopeBuilder.build(self.autoexecPath)
            autoexecResult = self.globalScope.exec(currentConnectionFrame.env)

            for autoexecResultLine in autoexecResult:
                self.writeToCurrentFrameConsole(autoexecResultLine)

            self.writeToCurrentFrameConsole("Read '{0}' script ({1} functions; {2} instructions).\n".format(
                self.autoexecPath, 
                self.globalScope.getNumberOfFunctions(),
                self.globalScope.getNumberOfInstructions()))
        except Exception as e:
            print(str(e))
            self.writeToCurrentFrameConsole(str(e))

    def writeToCurrentFrameConsole(self, msg):
        self.connectionFrames[self.getCurrentConnectionIndex()].writeToConsole(msg)
    
    def getLabelEntry(self): return self.configPanelEntries["defaultLabel"][1]
    def getHostEntry(self): return self.configPanelEntries["defaultHost"][1]
    def getPortEntry(self): return self.configPanelEntries["defaultPort"][1]
    def getCommandRegexEntry(self, index): return self.configPanelEntries[self.config.cmdPatternFormat.format(index)][1]
    def getPreConnectCommandEntry(self): return self.configPanelEntries["defaultPreConnectCommand"][1]
    def getCommandDateFormatEntry(self): return self.configPanelEntries["timeStampDateFormat"][1]

    def updateConfigPanel(self):
        for key, (label, entry) in self.configPanelEntries.items():
            if key in self.defaultGlobalSettings:
                entry.delete(0, "end")
                entry.insert(0, self.defaultGlobalSettings[key][0])

        cmdPatterns = self.config.getListOfCommandPatterns()
        for i, cmdPattern in enumerate(cmdPatterns):
            patternEntry = self.getCommandRegexEntry(i)
            patternEntry.delete(0, "end")
            patternEntry.insert(0, cmdPattern)

    def getConfig(self):
        return self.config

    def parseListOfCommands(self, receivedLines, listOfPatterns):
        compiledPatterns = [ re.compile(pattern) for pattern in listOfPatterns ]
        listOfCommands = []

        for command in receivedLines:
            command = command.strip("\r\n")

            for compiledPattern in compiledPatterns:
                matched = compiledPattern.search(command)

                if matched:
                    listOfCommands.append(matched.group(1))
                    # Skip to next command:
                    break

        return listOfCommands
    
    def getDefaultSectionConfig(self):
        return OrderedDict([
            ("host", self.getHostEntry().get()),
            ("port", self.getPortEntry().get()),
        ])
    
    def applyConfig(self):
        config = self.config.getContent()

        if config is None or len(config) == 0:
            self.addNewConnectionFrame(None)
            return
        
        for sectionName, section in config.items():
            if self.config.isTabSectionName(sectionName):
                self.addNewConnectionFrame(None, section)

            elif self.config.isCmdWidgetSectionName(sectionName):
                pass

            elif sectionName == self.config.globalSectionFormat:
                cmdPatterns = self.config.getListOfCommandPatterns()

                for i, pattern in enumerate(cmdPatterns):
                    self.getCommandRegexEntry(i).insert(0, pattern)

                for key, value in section.items():
                    # Update bool options:
                    if key in self.boolOptions:
                        self.boolOptions[key][1].set(value)

                    # Update text options:
                    if key in self.configPanelEntries:
                        entry = self.configPanelEntries[key][1]
                        entry.delete(0, "end")
                        entry.insert(0, value)

    def addNewConnectionFrame(self, parent=None, sectionContent=None):
        parent = parent if parent else self.mainPanel
        numberOfConnectionFrames = len(self.connectionFrames)
        sectionContent = sectionContent if sectionContent else self.getDefaultSectionConfig()

        if numberOfConnectionFrames < self.maxNumberOfConnections:
            connectionFrame = ConnectionFrame(parent, rootFrame=self, sectionContent=sectionContent)

            self.connectionNotebook.add(connectionFrame, text=connectionFrame.getTitle())
            self.connectionFrames.append(connectionFrame)
            connectionFrame.onCreate()
    
    def getCurrentConnectionIndex(self):
        selected = self.connectionNotebook.select()
        index = self.connectionNotebook.index(selected)
        return index
        # return self.connectionNotebook.index("current")
    
    def getCurrentConnectionFrame(self):
        index = self.getCurrentConnectionIndex()
        return self.connectionFrames[index]
    
    def getIndexOfConnectionFrame(self, frame):
        return self.connectionFrames.index(frame)

    def closeConnectionFrame(self):
        numberOfConnectionFrames = len(self.connectionFrames) 

        if numberOfConnectionFrames > 1:
            index = self.getCurrentConnectionIndex()
            self.connectionNotebook.forget(index)
            self.connectionFrames.remove(self.connectionFrames[index])

    def getListOfTabTitles(self):
        return [frame.getTitle() for frame in self.connectionFrames]

    def refreshTabTitle(self, index):
        newTitle = self.connectionFrames[index].getTitle()
        self.connectionNotebook.tab(index, text=newTitle)

    def refreshCurrentTabTitle(self):
        self.refreshTabTitle(self.getCurrentConnectionIndex())

    def refreshTabTitles(self):
        for i in range(self.connectionNotebook.tabs()):
            self.refreshTabTitle(i)

    def saveConnectionHistory(self):
        for connectionFrame in self.connectionFrames:
            connectionFrame.saveHistory()

    def execCommandOnAllConnections(self, command):
        output = []

        for connectionFrame in self.connectionFrames:
            if not connectionFrame.telnet.isConnected():
                continue
            connectionName = connectionFrame.getTitle()

            try:
                instruction = TScriptCommandParser.build(command)
                receivedLines = instruction.exec(connectionFrame.env)
            except Exception as e:
                receivedLines = ["{0}\n".format(str(e))]

            output.append((connectionName, receivedLines))

        return output
    
    def callMethodOnConnectionFrames(self, connectionFrameMethodName):
        for connectionFrame in self.connectionFrames:
            getattr(connectionFrame, connectionFrameMethodName)()

    def onSaveButtonPressed(self):
        self.config.save()

    def onConnectionTabChanged(self, event):
        index = self.getCurrentConnectionIndex()
        selectedTabFrame = self.connectionFrames[index]
        selectedTabFrame.inputEntry.focus_set()
    
    def onExit(self, root):
        self.config.save()
        self.saveConnectionHistory()
        root.destroy()

def main():
    root = Tk()
    root.geometry("1024x768")
    rootFrame = TelnetGui(root)
    root.protocol("WM_DELETE_WINDOW", lambda: rootFrame.onExit(root))
    root.mainloop()

if __name__ == "__main__":
    main()

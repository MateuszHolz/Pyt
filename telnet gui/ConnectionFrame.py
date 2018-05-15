import traceback
import _thread
import time
import sys
import os
import re

from collections import OrderedDict
from tkinter import ttk
from tkinter import *

from NaiveCompletionEngine import *
from PortScannerThread import *
from BookmarksManager import *
from HistoryManager import *
from TelnetManager import *
from TelnetEnvironment import *
from TkTools import *
from TScript import *
from SyntaxHighlightings import *

class ConnectionFrame(ttk.Frame):

    rootFrame = None
    connectionEntries = None
    connection = None
    options = None
    buttons = None
    inputEntry = None

    bookmarks = BookmarksManager()
    syntaxHighlighting = "telnetOutput"

    history = HistoryManager()
    historyFilePath =".telnetGuiHistory_{0}"

    telnetScanPortTimeout = 6
    lastListOfCommands = []
    completionEngine = NaiveCompletionEngine()

    currentHistoryIndex = 0

    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent)

        self.rootFrame = kwargs["rootFrame"]
        self.scannerThread = PortScannerThread(self)
        self.telnet = TelnetManager()
        self.env = TelnetEnvironment(self.telnet, self)

        self.optionDefinitions = [
            ("Label", "Label"),
            ("Host", "Host"),
            ("Port", "Port"),
            ("PreConnectCommand", "Pre-connect command"),
        ]
        
        self.runConnectThread = lambda: _thread.start_new_thread(self.onConnectButtonPressed, tuple())
        self.runCommandThread = lambda: _thread.start_new_thread(self.onExecuteButtonPressed, tuple())
        self.runGlobalExecThread = lambda: _thread.start_new_thread(self.onGlobalExec, tuple())

        # Actions related with keyPress events:
        self.inputKeyPressedActions = {
            r'\t':      self.onCompleteCommand,
            r'\r':      self.runCommandThread,
        }

        # Actions related with commands:
        self.onCommandActions = {
            "\n":       self.onCommandsReceived,
        }

        # List of upper buttons:
        self.upperButtonsLeft = [ 
            ("Connect",             self.buildGlobalExecDecorator("runConnectThread")),
            ("Disconnect",          self.buildGlobalExecDecorator("onDisconnectButtonPressed")),
            ("Sort commands",       self.buildGlobalExecDecorator("onSortButtonPressed")),
            ("Clear history",       self.buildGlobalExecDecorator("onClearHistoryButtonPressed")),
            ("Refresh commands",    self.buildGlobalExecDecorator("onRefreshCommandsButtonPressed")),
        ]

        self.upperButtonsRight= [ 
            ("Close",               self.onCloseButtonPressed),
            ("New",                 self.onNewButtonPressed),
        ]

        # List of lower buttons:
        self.lowerButtons = [ 
            ("Exec",        self.runCommandThread),
            ("Global Exec", self.runGlobalExecThread),
            ("Clear",       self.onClearButtonPressed),
        ]

        self.loadLayout()

        if kwargs["sectionContent"]:
            self.applySectionConfig(kwargs["sectionContent"])

        self.writeWelcomeMsg()

    def writeWelcomeMsg(self):
        self.writeToConsole("Execute 'help' to show list of built-in commands.\n")
    
    def buildGlobalExecDecorator(self, methodName):
        def decorator():
            if self.globalExecEnabled.get():
                self.rootFrame.callMethodOnConnectionFrames(methodName)
            else:
                getattr(self, methodName)()

        return decorator

    def getActiveListboxEntry(self, listbox):
        selection = listbox.curselection()
        if len(selection) == 0:
            return None
        return int(selection[0])

    def onHistoryAddButtonPressed(self):
        index = self.getActiveListboxEntry(self.historyListbox)

        if index is None:
            return

        history = self.history.getContent()
        self.bookmarks.append(self.currentBookmark.get(), history[index])
        self.fillBookmarksListbox()

    def onHistoryRemoveButtonPressed(self):
        index = self.getActiveListboxEntry(self.historyListbox)
        if index is None:
            return
        history = self.history.getContent()
        self.history.removeEntry(history[index])
        self.fillHistoryListbox()
        self.saveHistory()

    def buildHistoryBookmarksButtonFrame(self, parent):# {{{
        buttonsFrame = ttk.Frame(parent)
        buttonsFrame.pack(side=BOTTOM, fill=X)
        bookmarkButton = Button(buttonsFrame, text="Add to Bookmarks", command=self.onHistoryAddButtonPressed)
        bookmarkButton.pack(side=LEFT, fill=X, expand=True)
        removeFromHistoryButton = Button(buttonsFrame, text="Remove", command=self.onHistoryRemoveButtonPressed)
        removeFromHistoryButton.pack(side=RIGHT, fill=X, expand=True)# }}}

    def buildLabeledListbox(self, parent, title, buttonsFrameFunction=None):#{{{
        frame = ttk.Frame(parent)
        frame.pack(fill=BOTH, expand=True)
        listbox = Listbox(frame)
        listboxTitle = Label(frame, text=title, bg="grey", fg="white")
        listboxTitle.pack(side=TOP, padx=5, pady=5, fill=X)

        if buttonsFrameFunction:
            buttonsFrameFunction(frame)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=listbox.yview)

        listbox.config(yscrollcommand=scrollbar.set)
        listbox.pack(fill=BOTH, expand=True)

        return (listbox, frame)
    # }}}

    def buildListbox(self, parent, panelSide, title="", buttonsFrameFunction=None):# {{{
        listboxFrame = ttk.Frame(parent)
        listboxFrame.pack(side=panelSide, fill=BOTH)
        (listbox, frame, _) = buildLabeledListbox(listboxFrame, title, buttonsFrameFunction)

        return (listbox, listboxFrame)
    # }}}

    def onListboxItemSelected(self, event):
        self.copyActiveListboxValueToEntry(event.widget)
        self.inputEntry.focus_set()

    def onBookmarkItemSelected(self, event):
        selection = event.widget.curselection()
        selectedIndex = int(selection[0]) if len(selection) > 0 else 0

        self.clearInputEntry()
        self.inputEntry.insert(0, self.bookmarks.getCommandByIndex(selectedIndex))
        self.inputEntry.focus_set()

    def loadLayout(self):# {{{
        mainFrame = ttk.Frame(self)

        self.options = []
        for optionEntryLabel, optionEntryDescription in self.optionDefinitions:
            self.options.append(buildOptionLabel(self, optionEntryLabel, optionEntryDescription))

        self.options = OrderedDict(self.options)
        self.options["Label"][1].bind('<FocusOut>', lambda event: self.rootFrame.refreshCurrentTabTitle())

        # List of commands:
        (self.commandsListbox, leftListboxFrame, _) = buildListbox(mainFrame, LEFT, "Commands")
        # List of commands in history:
        (self.historyListbox, rightListboxFrame, _) = buildListbox(mainFrame, RIGHT, "History", self.buildHistoryBookmarksButtonFrame)
        # List of bookmarks:
        (self.bookmarksListbox, bookmarksFrame, _) = buildLabeledListbox(rightListboxFrame, "Bookmarks")

        listboxDefs = [
            (self.commandsListbox,  lambda event: self.onListboxItemSelected(event)),
            (self.historyListbox,   lambda event: self.onListboxItemSelected(event)), 
            (self.bookmarksListbox, lambda event: self.onBookmarkItemSelected(event)),
        ]

        for (listbox, listboxItemSelectedCallback) in listboxDefs:
            listbox.config(width=30)
            listbox.bind('<Double-Button-1>', listboxItemSelectedCallback)
            listbox.bind('<FocusIn>', lambda event: self.onListboxFocusIn(event))
            # TODO: Check why binding lambda to key event does not work in loop (reference to listboxContent):
            # listbox.bind('<Key>', lambda event: self.onListboxKeyPressed(event, listboxContent))

        self.commandsListbox.bind('<Key>', lambda event: self.onListboxKeyPressed(event, self.lastListOfCommands))
        self.historyListbox.bind('<Key>', lambda event: self.onListboxKeyPressed(event, self.history.content))
        self.bookmarksListbox.bind('<Key>', lambda event: self.onListboxKeyPressed(event, self.bookmarks.bookmarks))

        # Bookmarks selection menu:
        listOfBookmarks = self.bookmarks.getFilenames()
        self.currentBookmark = StringVar()
        self.currentBookmark.set(listOfBookmarks[0] if listOfBookmarks else "<Bookmarks not found>")
        bookmarksMenu = OptionMenu(bookmarksFrame, self.currentBookmark, *listOfBookmarks if listOfBookmarks else "-", command=self.onBookmarkChanged)
        bookmarksMenu.pack(side=TOP, fill=X)

        # Pre-connect cmd enabled checkbox:
        self.preConnectCmdEnabled = IntVar()
        preConnectCmdCheckbox = Checkbutton(
                self.options["PreConnectCommand"][1],
                text="",
                variable=self.preConnectCmdEnabled,
                onvalue=1, offvalue=0)
        preConnectCmdCheckbox.pack(side=RIGHT)

        # Output window:
        (outputFrame, self.outputText) = buildOutputFrame(mainFrame)
        SyntaxHighlightings.setTags(self.outputText)
        self.outputText.pack(side=BOTTOM, fill=BOTH, expand=True)

        inputFrame = ttk.Frame(mainFrame)
        inputFrame.pack(fill=X)

        # Main command line input entry:
        self.inputEntry = Entry(inputFrame)
        self.inputEntry.bind("<Tab>", lambda event: self.onInputEntryKeyPressed(event))
        self.inputEntry.bind('<Key>', lambda event: self.onInputEntryKeyPressed(event))
        self.inputEntry.bind('<Down>', self.onInputEntryNextHistoryEntry)
        self.inputEntry.bind('<Up>', self.onInputEntryPrevHistoryEntry)
        self.inputEntry.bind('<Shift-Return>', lambda event: self.onShiftEnterPressed(event))
        self.inputEntry.pack(side=RIGHT, fill=X, expand=True)
        self.inputEntry.focus_set()

        upperButtonPanel = Frame(outputFrame)
        upperButtonPanel.pack(side=TOP, fill=X)

        lowerButtonPanel = Frame(inputFrame)
        lowerButtonPanel.pack(side=RIGHT)

        self.globalExecEnabled = IntVar()
        globalCheckbox = Checkbutton(
                upperButtonPanel,
                text="Global",
                variable=self.globalExecEnabled,
                onvalue=1, offvalue=0)
        globalCheckbox.pack(side=LEFT)

        self.buttons = OrderedDict()
        for (label, callback) in self.upperButtonsLeft:
            button = Button(upperButtonPanel, text=label, command=callback)
            button.pack(side=LEFT)
            self.buttons[label] = button

        for (label, callback) in self.upperButtonsRight:
            button = Button(upperButtonPanel, text=label, command=callback)
            button.pack(side=RIGHT)
            self.buttons[label] = button

        for (label, callback) in self.lowerButtons:
            button = Button(lowerButtonPanel, text=label, command=callback)
            button.pack(side=RIGHT)
            self.buttons[label] = button

        mainFrame.pack(expand=True, fill=BOTH)
    # }}}

    def getLabelEntry(self):
        return self.options["Label"][1]

    def getHostEntry(self):
        return self.options["Host"][1]

    def getPortEntry(self):
        return self.options["Port"][1]

    def getPreConnectCommandEntry(self):
        return self.options["PreConnectCommand"][1]
    
    def getConnectButton(self):
        return self.buttons["Connect"]

    def getConnectionAttributes(self):
        return (self.getHostEntry().get(), self.getPortEntry().get())
    
    def getListOfCommandCompletions(self):
        result = list(self.lastListOfCommands)
        result.extend([function.name for function in self.rootFrame.globalScope.getFunctions()])
        result.extend([alias for (alias, _) in self.bookmarks.getAliases()])
        print(result)
        return result

    def onCompleteCommand(self):
        typedText = self.inputEntry.get()
        (completions, intersection) = self.completionEngine.extract(self.getListOfCommandCompletions(), typedText)
        numberOfCompletions = len(completions)

        if numberOfCompletions == 1:
            self.setInputEntryText(completions[0])
            return

        # Complete current text to shortest substring of all available commands:
        if intersection != "":
            self.setInputEntryText(intersection)

        # Print list of completions:
        self.writeToConsole("\n{0}\n".format("    ".join(completions)))

        self.inputEntry.focus()

    def getListboxIndexByValue(self, listbox, value):
        listboxValues = getListboxValues(listbox)
        return listboxValues.index(value) if value in listboxValues else None

    def onListboxKeyPressed(self, event, commandsToComplete):
        key = repr(event.char).strip("'")
        listbox = event.widget

        # FIXME: Separate listbox completion:
        if len(commandsToComplete) == 0:
            return
        if key == r'\r':
            self.copyActiveListboxValueToEntry(listbox)
            return
        if not hasattr(listbox, 'previousInsertTime'):
            listbox.previousInsertTime = time.time()
        if not hasattr(listbox, 'completionBuffer'):
            listbox.completionBuffer = []
        
        timeoutPassed = (time.time() - listbox.previousInsertTime) > 2.0

        # Clear buffer when escape button was pressed:
        if timeoutPassed or (not key.isalpha()):
            listbox.completionBuffer = []
        if not key.isalpha():
            return

        listbox.completionBuffer.append(key)
        typedText = "".join(listbox.completionBuffer).strip(" ")

        if typedText == "" or (not typedText.isalpha()):
            return

        (completions, _) = self.completionEngine.extract(commandsToComplete, typedText, ignoreCase=True)
        
        if len(completions) > 0:
            index = self.getListboxIndexByValue(listbox, completions[0])
            if index is not None:
                listbox.selection_clear(0, END)
                listbox.selection_set(index)
                listbox.see(index)

        listbox.previousInsertTime = time.time()

    def onListboxFocusIn(self, event):
        event.widget.completionBuffer = []

    def onInputEntryKeyPressed(self, event):
        key = repr(event.char).strip("'")

        if key in self.inputKeyPressedActions:
            self.inputKeyPressedActions[key]()
            # Restore focus to input entry when tab button is pressed:
            # http://stackoverflow.com/questions/1450180/change-the-focus-from-one-text-widget-to-another
            return "break"
        else:
            return ""

    def onInputEntryNextHistoryEntry(self, event):
        previousInputEntryContent = self.inputEntry.get()
        self.setInputEntryText(self.history.getEntry(self.currentHistoryIndex))

        if self.currentHistoryIndex > 0:
            self.currentHistoryIndex = self.currentHistoryIndex - 1

    def onInputEntryPrevHistoryEntry(self, event):
        previousInputEntryContent = self.inputEntry.get()
        self.setInputEntryText(self.history.getEntry(self.currentHistoryIndex))

        if self.currentHistoryIndex + 1 != self.history.getSize():
            self.currentHistoryIndex = self.currentHistoryIndex + 1

    def onShiftEnterPressed(self, event):
        self.runGlobalExecThread()

    def runTelnetPortScannerThread(self):
        self.scannerThread.run()

    def onCreate(self):
        self.history.buildFromFile(self.getHistoryFilename())
        self.fillHistoryListbox()
        self.fillBookmarksListbox()
    
    def fillCommandListbox(self, commands):
        fillListbox(self.commandsListbox, commands)

    def fillHistoryListbox(self):
        fillListbox(self.historyListbox, self.history.getContent())

    def fillBookmarksListbox(self):
        fillListbox(self.bookmarksListbox, self.bookmarks.get())

    def writeTelnetMsgToConsole(self, msg):
        (host, port) = (self.getHostEntry().get(), self.getPortEntry().get())
        self.writeToConsole("{0} {1}:{2}: {3}\n".format(SyntaxHighlightings.syntaxMsgPrefix, host, port, msg))
    
    def resetOutputScrollbar(self):
        self.outputText.see(END)

    def getTitle(self):
        (host, port) = (self.getHostEntry().get(), self.getPortEntry().get())
        label = self.getLabelEntry().get().strip()
        newTitle = ""

        if label != "":
            newTitle = label.replace("$HOST", host)
            newTitle = newTitle.replace("$PORT", port)
            newTitle = newTitle.replace("$STATUS2", "*" if self.telnet.isConnected() else "-")
            newTitle = newTitle.replace("$STATUS", "Connected" if self.telnet.isConnected() else "Disconnected")
        else:
            newTitle = "{0}:{1}".format(host, port)

        return newTitle

    def clearInputEntry(self):
        self.inputEntry.delete(0, "end")

    def setInputEntryText(self, newText):
        self.clearInputEntry()
        self.inputEntry.insert(0, newText)

    def copyActiveListboxValueToEntry(self, listbox):
        selection = listbox.curselection()
        selectedIndex = int(selection[0]) if len(selection) > 0 else 0

        self.clearInputEntry()
        self.inputEntry.insert(0, listbox.get(selectedIndex))

    def onNewButtonPressed(self):
        self.rootFrame.addNewConnectionFrame()

    def printGlobalExecOutput(self, command):
        output = self.rootFrame.execCommandOnAllConnections(command)
        for (connectionName, connectionOutput) in output:
            msg = "{0}: {1}\n".format(connectionName, command)
            textSeparator = "{0}\n".format(len(msg) * "-")
            self.writeToConsole(textSeparator)
            self.writeToConsole(msg)
            self.writeToConsole(textSeparator)
            for line in connectionOutput:
                self.writeToConsole(line)

        if self.env.lastCommandSuccess:
            self.appendToHistory(command)

        self.highlightConsoleOutput()

    def onBookmarkChanged(self, event):
        bookmarkFile = self.currentBookmark.get()
        self.bookmarks.reloadFile(bookmarkFile)
        fillListbox(self.bookmarksListbox, self.bookmarks.get())

    def onGlobalExec(self):
        command = self.inputEntry.get()
        self.writeToConsole("Receiving output from all connections for command='{0}'...\n".format(command))
        _thread.start_new_thread(lambda: self.printGlobalExecOutput(command), tuple())
        self.clearInputEntry()

    def onClearButtonPressed(self):
        self.outputText.config(state=NORMAL)
        self.outputText.delete(1.0, END)
        self.outputText.config(state=DISABLED)

    def onRefreshCommandsButtonPressed(self):
        if not self.telnet.isConnected():
            self.telnet.connect(*self.getConnectionAttributes())

        self.sendAndHandleCommand("\n")

    def onSortButtonPressed(self):
        self.lastListOfCommands.sort()
        self.fillCommandListbox(self.lastListOfCommands)

    def onClearHistoryButtonPressed(self):
        self.history.clear()
        self.saveHistory()
        self.fillHistoryListbox()

    def onCloseButtonPressed(self):
        self.rootFrame.closeConnectionFrame()
        self.rootFrame.getConfig().save()

    def onDisconnectButtonPressed(self):
        if self.telnet.isConnected():
            self.telnet.disconnect()
        else:
            self.writeToConsole("No active connection.\n")

    def highlightConsoleOutput(self):
        if not self.rootFrame.enabledSyntaxHighlight.get():
            return

        SyntaxHighlightings.apply(self.outputText, self.syntaxHighlighting)

    def writeToConsole(self, line):
        self.outputText.config(state=NORMAL)
        self.outputText.insert(END, line)
        self.resetOutputScrollbar()
        self.outputText.config(state=DISABLED)

    def execPreConnectCommand(self):
        preConnectCmd = self.rootFrame.getPreConnectCommandEntry().get()
        self.writeToConsole("Executing pre-connect command:\n$ '{0}'\n".format(preConnectCmd))
        preConnectCmdExitCode = os.system(preConnectCmd)

        if preConnectCmdExitCode != 0:
            self.writeToConsole("Pre-connect command exited with code: {0}\n".format(preConnectCmdExitCode))

    def writeCurrentCommandToConsole(self, command):
        timeStampFormat = self.rootFrame.getCommandDateFormatEntry().get()
        msg = "{0} > {1}\n".format(time.strftime(timeStampFormat), command)
        consoleDecoration = "{0}\n".format(len(msg) * "-")

        self.writeToConsole(consoleDecoration)
        self.writeToConsole(msg)
        self.writeToConsole(consoleDecoration)

    def appendToHistory(self, line):
        self.history.append(line)
        self.fillHistoryListbox()
    
    def onCommandsReceived(self, receivedLines):
        listOfCommandPatterns = self.rootFrame.getConfig().getListOfCommandPatterns()
        listOfParsedCommands = self.rootFrame.parseListOfCommands(receivedLines, listOfCommandPatterns)
        self.lastListOfCommands = list(listOfParsedCommands)

        if len(listOfParsedCommands) > 0:
            if self.rootFrame.enabledCmdSort.get():
                listOfParsedCommands.sort()

            self.fillCommandListbox(listOfParsedCommands)
        else:
            self.writeTelnetMsgToConsole("Received zero-length data, try to reconnect.\n")
            self.telnet.disconnect()

    def onAnyCommandFinished(self, command, receivedLines):
        # Refresh history index:
        self.currentHistoryIndex = 0

        for line in receivedLines:
            self.writeToConsole(line)
    
        if self.env.lastCommandSuccess:
            self.appendToHistory(command)

        self.highlightConsoleOutput()

    def sendAndHandleCommand(self, command):
        if command == "\n":
            receivedLines = self.telnet.sendCommand(command)
        else:
            try:
                instruction = TScriptCommandParser.build(command)
                receivedLines = instruction.exec(self.env)
            except Exception as e:
                receivedLines = ["{0}\n".format(str(e))]

        # Execute action related with command:
        if command in self.onCommandActions:
            self.onCommandActions[command](receivedLines)

        self.onAnyCommandFinished(command, receivedLines)

    def onExecuteButtonPressed(self):
        command = self.inputEntry.get()

        self.clearInputEntry()
        self.writeCurrentCommandToConsole(command)
        self.sendAndHandleCommand(command)

    def onConnectButtonPressed(self):
        if self.telnet.isConnected():
            return

        if self.preConnectCmdEnabled.get():
            self.execPreConnectCommand()

        (host, port) = (self.getHostEntry().get(), self.getPortEntry().get())

        try:
            self.telnet.connect(*self.getConnectionAttributes())
            self.writeTelnetMsgToConsole("Receiving list of commands...")
            self.sendAndHandleCommand("\n")
            self.writeTelnetMsgToConsole("Calling onConnect()...")
            self.sendAndHandleCommand("onConnect")
            self.runTelnetPortScannerThread()
            self.rootFrame.refreshCurrentTabTitle()
        except ConnectionRefusedError as e:
            self.writeTelnetMsgToConsole(str(e))
        except Exception as e:
            self.writeTelnetMsgToConsole(str(e))
            self.writeTelnetMsgToConsole(traceback.format_exc())

    def getIndex(self):
        return self.rootFrame.getIndexOfConnectionFrame(self)

    def getHistoryFilename(self):
        index = self.getIndex()
        return self.historyFilePath.format(index)

    def saveHistory(self):
        self.history.saveToFile(self.getHistoryFilename())
    
    def getConfig(self):
        result = []

        fields = OrderedDict([
            ("label", self.getLabelEntry().get()),
            ("host", self.getHostEntry().get()),
            ("port", self.getPortEntry().get()),
            ("preConnectCommand", self.getPreConnectCommandEntry().get()),
            ("preConnectCommandEnabled", str(self.preConnectCmdEnabled.get())),
            ("bookmarksSet", self.currentBookmark.get())
        ])

        for fieldName, fieldValue in fields.items():
            if fieldValue:
                result.append("{0} = {1}".format(fieldName, fieldValue))

        return "\n".join(result)

    def applySectionConfig(self, sectionContent):
        items = OrderedDict([
            ("label", self.getLabelEntry()),
            ("host", self.getHostEntry()),
            ("port", self.getPortEntry()),
            ("preConnectCommand", self.getPreConnectCommandEntry()),
        ])

        for key, value in sectionContent.items():
            if key in items:
                items[key].insert(0, value)

        labelEntry = items["label"]
        if labelEntry.get().strip() == "":
            labelEntry.insert(0, self.rootFrame.getConfig().getGlobalSetting("defaultLabel"))

        def updateTkVariable(tkVariable, key):
            if key in sectionContent:
                tkVariable.set(sectionContent[key])

        updateTkVariable(self.preConnectCmdEnabled, "preConnectCommandEnabled")
        updateTkVariable(self.currentBookmark, "bookmarksSet")

        self.onBookmarkChanged(None)

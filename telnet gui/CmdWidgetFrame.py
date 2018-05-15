from TkTools import *
from BookmarksManager import *
from TScript import *
from ConnectionFrame import *
from CmdWidgetBaseFrame import *
from SyntaxHighlightings import *

"""
Collects output from one command, then send chosen line to the input of another command.
"""
class CmdWidgetFrame(CmdWidgetBaseFrame):
    itemSymbol = "$$"

    sectionEntries = OrderedDict([
        ("listBuildCommand",    "Command used to collect list of items."),
        ("listItemCommand",     "OnItemClick command, {0} denotes item.".format(itemSymbol)),
    ])

    def applyConfig(self):
        self.itemLabel.config(text=self.listItemTitle)
        self.buildButton.config(text=self.listBuildDescription)
        self.statusLabel.config(text=self.hint)
        self.outputLabel.config(text=self.listBuildDescription)

    """
    @param parent 
        Parent of this widget (ttk.Frame).
    @param section
        Definition of command widget (section from config file).
    @param rootFrame
        TelnetGui object.
    """
    def __init__(self, **kwargs):
        CmdWidgetBaseFrame.__init__(self, **kwargs)

        self.outputHighlighting = getattr(self, "outputHighlighting", None)

        panel = ttk.Panedwindow(self)
        for key, description in self.sectionEntries.items():
            (_, (frame, entry)) = buildOptionLabel(panel, key, description)
            entryState = NORMAL if self.isEntryEditable(key) else DISABLED
            entry.delete(0, "end")
            entry.insert(0, getattr(self, key, ""))
            entry.config(state=entryState)
            entry.key = key
            entry.bind('<Key>', lambda event: self.onEntryKeyPressed(event))
            panel.add(frame)

        panel.pack(side=TOP, fill=X)

        (self.itemListbox, self.fileListboxFrame, self.itemLabel) = buildListbox(self, LEFT, "")
        (outputFrame, self.outputText) = buildOutputFrame(self)

        SyntaxHighlightings.setTags(self.outputText)
    
        self.buildButton = Button(self.fileListboxFrame, text="", command=self.onBuildButtonPressed)
        self.buildButton.pack(side=LEFT, fill=X, expand=True)

        self.outputLabel = Label(outputFrame, text="-", bg="grey", fg="white")
        self.outputLabel.pack(side=TOP, padx=5, pady=5, fill=X)

        self.statusLabel = Label(outputFrame, text="<Choose file from list>", bg="grey", fg="white", anchor=W)
        self.statusLabel.pack(side=BOTTOM, padx=5, pady=5, fill=X)

        self.itemListbox.bind('<Double-Button-1>', lambda event: self.onListboxDoubleButtonPressed(event))
        self.itemListbox.config(width=40)

        self.outputText.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.applyConfig()

    def onEntryKeyPressed(self, event):
        widget = event.widget
        newEntryValue = widget.get()
        setattr(self, widget.key, newEntryValue)
        print("onEntryKeyPressed: {0} = {1}".format(widget.key, newEntryValue))

    def clearOutput(self):
        self.outputText.delete(1.0, END)

    def setMessage(self, msg):
        self.statusLabel.config(text=msg)
    
    def buildListOfItems(self):
        cmdResult = self.getCommandResult(self.listBuildCommand)

        result = []

        for line in cmdResult:
            strippedLine = line.strip()

            if strippedLine:
                result.append(strippedLine)

        return result
    
    def execItemCommand(self, item):
        commandForItem = self.listItemCommand.replace(self.itemSymbol, item)
        cmdResult = "".join(self.getCommandResult(commandForItem))

        self.clearOutput()
        self.setMessage("Output built from '{0}' command.".format(commandForItem))
        self.outputText.insert(END, "".join(cmdResult))
        SyntaxHighlightings.apply(self.outputText, self.outputHighlighting)

    def onBuildButtonPressed(self):
        self.listOfItems = self.buildListOfItems()
        fillListbox(self.itemListbox, self.listOfItems)

    def getListbox(self):
        return self.itemListbox
    
    def getText(self):
        return self.outputText

    def clearOutput(self):
        self.outputText.delete(1.0, END)

    def setMessage(self, msg):
        self.statusLabel.config(text=msg)

    def onListboxDoubleButtonPressed(self, event):
        listbox = event.widget
        selection = listbox.curselection()
        selectedIndex = int(selection[0]) if len(selection) > 0 else 0

        self.execItemCommand(self.listOfItems[selectedIndex])

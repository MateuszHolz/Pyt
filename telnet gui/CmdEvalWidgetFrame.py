from TkTools import *
from BookmarksManager import *
from TScript import *
from CmdWidgetBaseFrame import *
from SyntaxHighlightings import *

from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror

class CmdEvalWidgetFrame(CmdWidgetBaseFrame):
    itemSymbol = "$$"
    sectionEntries = [
        "outputCommand"
    ]

    def applyConfig(self):
        self.evalButton.config(text=self.outputBuildDescription)
        self.loadButton.config(text=self.loadScriptButtonLabel)
        self.inputLabel.config(text=self.inputDescription)
        self.outputLabel.config(text=self.outputDescription)

    def fillTextWidget(self, widget, lines):
        widget.delete(1.0, END)
        widget.insert(END, "".join(lines))
        widget.see(END)

    def onLoadButtonPressed(self):
        filename = askopenfilename()

        with open(filename, "r") as f:
            lines = f.readlines()
        
        self.fillTextWidget(self.inputText, lines)
        SyntaxHighlightings.apply(self.inputText, self.inputHighlighting)

    def onEvalButtonPressed(self):
        codeToEval = self.inputText.get("1.0", END)

        if self.joinLines:
            codeToEval = codeToEval.replace("\n", " ")

        evalCommand = self.outputCommand.replace(self.itemSymbol, codeToEval)

        print("CmdMultilineWidget:onEvalButtonPressed(): '{0}'".format(evalCommand))

        cmdResult = self.getCommandResult(evalCommand)

        self.fillTextWidget(self.outputText, cmdResult)

        SyntaxHighlightings.apply(self.outputText, self.outputHighlighting)
    
    def onInputKeyPressed(self, event):
        SyntaxHighlightings.apply(self.inputText, self.inputHighlighting)

    def onEntryKeyPressed(self, event):
        widget = event.widget
        newEntryValue = widget.get()
        setattr(self, widget.key, newEntryValue)
        print("onEntryKeyPressed: {0} = {1}".format(widget.key, newEntryValue))

    def __init__(self, **kwargs):
        CmdWidgetBaseFrame.__init__(self, **kwargs)

        self.inputHighlighting = getattr(self, "inputHighlighting", None)
        self.outputHighlighting = getattr(self, "outputHighlighting", None)
        self.joinLines = (getattr(self, "joinLines", "") == "1")

        panel = ttk.Panedwindow(self)
        for key in self.sectionEntries:
            (_, (frame, entry)) = buildOptionLabel(panel, key, self.getEntryDescription(key))
            entryState = NORMAL if self.isEntryEditable(key) else DISABLED

            entry.delete(0, "end")
            entry.insert(0, getattr(self, key, ""))
            entry.config(state=entryState)
            entry.key = key
            entry.bind('<Key>', lambda event: self.onEntryKeyPressed(event))
            panel.add(frame)

        panel.pack(side=TOP, fill=X)

        (inputFrame, self.inputText) = buildOutputFrame(self)
        self.inputLabel = Label(inputFrame, text="InputLabel", bg="grey", fg="white")
        self.inputText.bind('<Shift-Return>', lambda event: self.onEvalButtonPressed())

        (outputFrame, self.outputText) = buildOutputFrame(self)
        self.outputLabel = Label(outputFrame, text="OutputLabel", bg="grey", fg="white")

        self.inputText.bind('<Key>', lambda event: self.onInputKeyPressed(event))

        SyntaxHighlightings.setTags(self.inputText)
        SyntaxHighlightings.setTags(self.outputText)

        self.evalButton = Button(outputFrame, text="", command=self.onEvalButtonPressed)
        self.evalButton.pack(side=BOTTOM, fill=X, expand=True)

        self.loadButton = Button(outputFrame, text="", command=self.onLoadButtonPressed)
        self.loadButton.pack(side=BOTTOM, fill=X, expand=True)

        self.inputLabel.pack(side=TOP, padx=5, pady=5, fill=X)
        self.inputText.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.outputLabel.pack(side=TOP, padx=5, pady=5, fill=X)
        self.outputText.pack(side=BOTTOM, fill=BOTH, expand=True)

        self.applyConfig()

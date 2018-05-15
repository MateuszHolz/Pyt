from FileEditorFrame import *
from SyntaxHighlightings import *

class TScriptFrame(FileEditorFrame):
    scriptsDirectory = "scripts"
    syntaxHighlighting = "tscript"

    def __init__(self, parent, rootFrame):
        FileEditorFrame.__init__(self, parent=parent, filesDirectory=self.scriptsDirectory, title="Scripts")
        self.rootFrame = rootFrame

        buttons = [
            ("Apply autoexec", self.onReloadAutoexecButtonPressed),
        ]

        for label, callback in buttons:
            button = Button(self.getFileListboxFrame(), text=label, command=callback)
            button.pack(side=LEFT, fill=X, expand=True)

    def onReloadAutoexecButtonPressed(self):
        self.rootFrame.readAutoexec()
        self.setMessage("Autoexec reloaded.")

    def applyHighlighting(self):
        SyntaxHighlightings.apply(self.outputText, self.syntaxHighlighting)

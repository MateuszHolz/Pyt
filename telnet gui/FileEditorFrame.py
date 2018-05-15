from TkTools import *
from BookmarksManager import *
from SyntaxHighlightings import *

from os import listdir
from os.path import isfile, isdir, join, abspath

class FileEditorFrame(ttk.Frame):
    def __init__(self, **kwargs):
        ttk.Frame.__init__(self, kwargs["parent"])

        self.filesDirectory = kwargs["filesDirectory"]

        (self.filesListbox, self.fileListboxFrame, _) = buildListbox(self, LEFT, kwargs["title"])
        (outputFrame, self.outputText) = buildOutputFrame(self)
        self.outputText.bind('<Key>', lambda event: self.onTextKeyPressed(event))
        SyntaxHighlightings.setTags(self.outputText)
    
        buttons = [
            ("Save", self.onSaveButtonPressed),
            ("Reload", self.onReloadButtonPressed),
        ]

        for label, callback in buttons:
            button = Button(self.fileListboxFrame, text=label, command=callback)
            button.pack(side=LEFT, fill=X, expand=True)

        self.filenameLabel = Label(outputFrame, text="-", bg="grey", fg="white")
        self.filenameLabel.pack(side=TOP, padx=5, pady=5, fill=X)

        self.statusLabel = Label(outputFrame, text="<Choose file from list>", bg="grey", fg="white", anchor=W)
        self.statusLabel.pack(side=BOTTOM, padx=5, pady=5, fill=X)

        self.filesListbox.bind('<Double-Button-1>', lambda event: self.onListboxDoubleButtonPressed(event))
        self.filesListbox.config(width=40)
        self.outputText.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.buildListOfFiles()

        self.currentFile = ""

    def getFileListboxFrame(self):
        return self.fileListboxFrame
    
    def onTextKeyPressed(self, event):
        self.applyHighlighting()

    def onSaveButtonPressed(self):
        self.saveContentToFile(self.currentFile)

    def onReloadButtonPressed(self):
        if self.currentFile:
            self.loadFile(self.currentFile)

    def getListbox(self):
        return self.filesListbox
    
    def getText(self):
        return self.outputText

    def clearOutput(self):
        self.outputText.delete(1.0, END)

    def setMessage(self, msg):
        self.statusLabel.config(text=msg)

    def saveContentToFile(self, filename):
        if self.currentFile == "":
            return

        content = self.outputText.get(1.0, END)
        try:
            with open(filename, "w") as f:
                f.write(content)
            self.setMessage("Saved to '{0}'.".format(filename))
        except Exception as e:
            self.setMessage(str(e))
            raise e

    def getContentOfFile(self, filename):
        content = []

        with open(filename, "r") as f:
            content = f.readlines()

        return content

    def loadFile(self, filename):
        self.currentFile = abspath(filename)

        try:
            content = self.getContentOfFile(self.currentFile)
        except Exception as e:
            self.setMessage(str(e))
            return

        self.clearOutput()
        self.outputText.insert(END, "".join(content))
        self.filenameLabel.config(text=self.currentFile)
        self.applyHighlighting()
        self.setMessage("Loaded {0} lines from '{1}'.".format(len(content), self.currentFile))

    def onListboxDoubleButtonPressed(self, event):
        listbox = event.widget
        selection = listbox.curselection()
        selectedIndex = int(selection[0]) if len(selection) > 0 else 0

        self.loadFile(self.listOfFiles[selectedIndex])

    def applyHighlighting(self):
        pass

    def buildListOfFiles(self):
        try:
            self.listOfFiles = FileEditorFrame.getListOfScripts(self.filesDirectory)
            fillListbox(self.getListbox(), self.listOfFiles)
        except Exception as e:
            print(str(e))
            self.listOfFiles = []
    
    def getListOfFiles(directory):
        path = abspath(directory)
        return [f for f in listdir(path) if isfile(join(path, f))]

    def getListOfScripts(directory):
        result = []
        path = abspath(directory)

        for f in listdir(path):
            fullpath = join(path, f)
            print("getListOfScripts({0}); file: {1}".format(directory, f))

            if isfile(fullpath):
                result.append("{0}/{1}".format(directory, f) if directory else f)
            elif isdir(fullpath):
                result.extend(FileEditorFrame.getListOfScripts("{0}/{1}".format(directory, f) if directory else f))

        return result

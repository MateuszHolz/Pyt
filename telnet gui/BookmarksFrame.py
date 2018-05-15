from FileEditorFrame import *
from SyntaxHighlightings import *

class BookmarksFrame(FileEditorFrame):
    syntaxHighlighting = "bookmarks"

    def __init__(self, parent):
        FileEditorFrame.__init__(self, parent=parent, filesDirectory=BookmarksManager.sourceDirectory, title="Bookmarks")

    def applyHighlighting(self):
        SyntaxHighlightings.apply(self.outputText, self.syntaxHighlighting)

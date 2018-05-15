from os import listdir
from os.path import isfile, join, abspath
from collections import OrderedDict

class BookmarksFile:
    def __init__(self, shortFilename):
        self.shortFilename = shortFilename
        self.build()

    def readBookmarkFileByName(self, bookmarkFile):
        bookmarkPath = join(abspath(BookmarksManager.sourceDirectory), bookmarkFile)
        result = []

        with open(bookmarkPath, "r") as f:
            lines = f.readlines()
        
        for line in lines:
            strippedLine = line.strip()

            if not strippedLine:
                continue

            aliasSym = ":"
            aliasSymIndex = strippedLine.find(aliasSym)
            if aliasSymIndex > 0 and strippedLine.count(aliasSym) == 1:
                (alias, command) = strippedLine.split(aliasSym)
                (alias, command) = (alias.strip(), command.strip())
                result.append((alias, command))
            else:
                result.append(("", strippedLine))

        print("[{0}]: Read {1} bookmarks.".format(bookmarkPath, len(result)))

        return result

    def build(self):
        self.bookmarks = self.readBookmarkFileByName(self.shortFilename)
    
    def save(self):
        bookmarkPath = join(abspath(BookmarksManager.sourceDirectory), self.shortFilename)

        if not self.bookmarks:
            return

        try:
            with open(bookmarkPath, "w") as f:
                for (alias, command) in self.bookmarks:
                    if alias:
                        f.write("{0}: \t\t{1}\n".format(alias, command))
                    else:
                        f.write("{0}\n".format(command))
        except Exception as e:
            print(str(e))

        print("[{0}]: Saved {1} lines bookmarks.".format(bookmarkPath, len(self.bookmarks)))

    def getCommandByIndex(self, index):
        bookmark = self.bookmarks[index] 
        return bookmark[1]

    def getAliases(self):
        return [ bookmark for bookmark in list(filter(lambda bookmark: bookmark[0], self.bookmarks)) ]
    
    def getAliasCommand(self, aliasToFind):
        for (alias, command) in self.getAliases():
            if alias == aliasToFind:
                return command
        return ""

    def isAlias(self, name):
        return name in [ alias for (alias, command) in self.getAliases() ]
    
    def get(self):
        return [ bookmark[0] if bookmark[0] else bookmark[1] for bookmark in self.bookmarks ]

    def append(self, line):
        self.bookmarks.append(("", line))
        self.save()

class BookmarksManager:
    sourceDirectory = "bookmarks"

    def __init__(self):
        self.buildListOfFiles()
        self.lastFile = ""

        if self.bookmarkFiles:
            self.buildBookmarks()
            self.lastFile = self.bookmarkFiles[0]

    def reloadFile(self, bookmarkFile):
        self.lastFile = bookmarkFile
        self.bookmarks[bookmarkFile].build()

    def getLastFile(self):
        return self.bookmarks[self.lastFile]

    def get(self):
        return self.getLastFile().get()

    def getCommandByIndex(self, index):
        return self.getLastFile().getCommandByIndex(index)
    
    def buildListOfFiles(self):
        try:
            self.bookmarkFiles = BookmarksManager.getListOfBookmarks(self.sourceDirectory)
        except Exception as e:
            print(str(e))
            self.bookmarkFiles = []

    def getListOfBookmarks(directory):
        path = abspath(directory)
        return [f for f in listdir(path) if isfile(join(path, f))]

    def buildBookmarks(self):
        self.bookmarks = OrderedDict()
        for bmark in self.bookmarkFiles:
            self.bookmarks[bmark] = BookmarksFile(bmark)

    def getFilenames(self):
        return self.bookmarkFiles

    def append(self, bookmarkFile, line):
        self.bookmarks[bookmarkFile].append(line)

    def isAlias(self, name):
        for (bmarkFile, bmark) in self.bookmarks.items():
            if bmark.isAlias(name):
                return True
        return False

    def getAliases(self):
        aliases = []

        for (bmarkFile, bmark) in self.bookmarks.items():
            aliases.extend(bmark.getAliases())

        return aliases

    def getAliasCommand(self, aliasToFind):
        cmd = ""

        for (bmarkFile, bmark) in self.bookmarks.items():
            cmd = bmark.getAliasCommand(aliasToFind)

            if cmd:
                break

        return cmd

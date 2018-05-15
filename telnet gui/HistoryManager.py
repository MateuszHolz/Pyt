from os.path import abspath

class HistoryManager:
    content = []

    def clear(self):
        self.content = []

    def getSize(self):
        return len(self.content)

    def getEntry(self, index):
        return self.content[index]

    def getContent(self):
        return self.content
    
    def append(self, line):
        line = line.strip()

        if line == "":
            return

        if self.content.count(line) == 0:
            # self.content.append(line)
            self.content = [line] + self.content
        else:
            index = self.content.index(line)
            self.content.remove(self.content[index])
            self.content = [line] + self.content

    def save(self, filename, content):
        try:
            with open(filename, "w") as f:
                for historyEntry in content:
                    f.write(historyEntry + "\n")
                print("[{0}]: Saved history file.\n".format(abspath(filename)))
        except Exception as exception:
            print(exception)

    def read(self, filename):
        history = []

        try:
            with open(filename, "r") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line != "":
                        history.append(line)
            print("[{0}]: Read {1} history entries.\n".format(abspath(filename), len(history)))
        except Exception:
            pass

        return history

    def removeEntry(self, line):
        if self.content and line in self.content:
            self.content = list(filter(lambda l: l != line, self.content))

    def saveToFile(self, filename):
        self.save(filename, self.content)

    def buildFromFile(self, filename):
        self.content = self.read(filename)

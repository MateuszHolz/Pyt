class unauthorizedIndex():
    print("initialzied class")
    def __init__(self):
        self.index = 0
    def addUnauthIndex(self):
        self.index += 1
    def getUnauthIndex(self):
        return self.index



d = unauthorizedIndex()
print(d)
d.addUnauthIndex()

print(d.getUnauthIndex())
d.addUnauthIndex()
print(d.getUnauthIndex())

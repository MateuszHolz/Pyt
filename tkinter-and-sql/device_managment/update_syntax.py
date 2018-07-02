from tkinter import *
import sqlite3 as sql
import main

class mainProgram():

	def __init__(self):
		self.window = Tk()
		self.db = main.DatabaseHandler()
		self.bottomFrame = Frame(self.window)
		self.bottomFrame.pack(side = BOTTOM)
		self.leftFrame = Frame(self.window)
		self.leftFrame.pack(side = LEFT)
		self.centerFrame = Frame(self.window)
		self.centerFrame.pack(side = LEFT)
		self.rightFrame = Frame(self.window)
		self.rightFrame.pack(side = RIGHT)
		self.patDict = {}
		self.applyChangesBtn = Button(self.bottomFrame, text = 'Apply new patterns', command = self.updatePattern)
		self.applyChangesBtn.pack(side = BOTTOM)
		self.setAllLabels()

		self.window.mainloop()

	def setAllLabels(self):
		patterns = self.db.getPatterns()
		if len(patterns) < 5:
			self.setDefaultSyntax()
			patterns = self.db.getPatterns()
		for i in self.db.getPatterns():
			l = Label(self.leftFrame, text = i[0])
			l.pack()
			kVar = StringVar()
			k = Entry(self.centerFrame, textvariable = kVar, state = 'readonly')
			kVar.set(i[1])
			k.pack(pady = 1)
			strVar = StringVar()
			e = Entry(self.rightFrame, textvariable = strVar)
			e.pack(pady = 1)
			self.patDict[i[0]] = [l, k, strVar, kVar]

	def updateLabels(self):
		for i in self.db.getPatterns():
			self.patDict[i[0]][3].set(i[1])

	def updatePattern(self):
		patterns = []
		for i, j in self.patDict.items():
			if j[2].get() is not '':
				self.db.updateRecord(table = 'patterns', newPattern = j[2].get(), cond = i)
		self.updateLabels()

	def setDefaultSyntax(self):
		syntaxTable = [
		('inventoryID', '^[0-9]{4}$'), 
		('deviceName', '^(?!\\s*$).+'), 
		('osVer', '^\\d+(\\.\\d+)*$'), 
		('resolution', '^\\d{3,4}x\\d{3,4}'), 
		('resolutionWithoutNB', '^\\d{3,4}x\\d{3,4}'), 
		('aspectRatio', '^\\d+(\\.\\d)?:\\d+$'), 
		('hardwareKeyTest', '^[A-Za-z0-9]{8}-([A-Za-z0-9]{4}-){3}[A-Za-z0-9]{20}-([A-Za-z0-9]{4}-){3}[A-Za-z0-9]{4}$'), 
		('deviceInfoAndroid', '^[A-Za-z0-9]{14,16}$'), 
		('macAddress', '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
		]
		for i in syntaxTable:
			self.db.addRecord('patterns', i)

if __name__ == '__main__':
	mainProgram()
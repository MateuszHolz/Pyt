from tkinter import *
import sqlite3 as sql
import main

class mainProgram():

	def __init__(self):
		self.window = Tk()
		self.db = main.databaseHandler()
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
		for i in self.db.getPatterns():
			l = Label(self.leftFrame, text = i[0])
			l.pack()
			lVar = StringVar()
			k = Label(self.centerFrame, textvariable = lVar)
			lVar.set(i[1])
			k.pack()
			strVar = StringVar()
			e = Entry(self.rightFrame, textvariable = strVar)
			e.pack(pady = 1)
			self.patDict[i[0]] = [l, k, strVar, lVar]

	def updateLabels(self):
		for i in self.db.getPatterns():
			self.patDict[i[0]][3].set(i[1])

	def updatePattern(self):
		patterns = []
		for i, j in self.patDict.items():
			if j[2].get() is not '':
				self.db.updateRecord(table = 'patterns', newPattern = j[2].get(), cond = i)
		self.updateLabels()

if __name__ == '__main__':
	mainProgram()
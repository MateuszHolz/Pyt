from tkinter import *
import sqlite3 as sql
import re

class mainWindow():

	def __init__(self):

		self.devicesData = []
		self.window = Tk()
		self.listBoxFrame = Frame(self.window)
		self.searchBoxFrame = Frame(self.window)
		self.searchFieldVar = StringVar()
		self.database = databaseHandler()

		self.btn1 = Button(self.window, text = 'createDb', command = self.database.createTable)
		self.btn2 = Button(self.window, text = 'viewDb', command = lambda: self.getListBoxData(self.database.viewDatabase()))
		self.btn3 = Button(self.window, text = 'Close', command = self.quit, height = 3)
		self.btn4 = Button(self.window, text = 'Add Record', command = lambda: addNewRecordWindow(self.window, self.database))
		self.btn5 = Button(self.searchBoxFrame, text = 'Search')
		self.inptField = Entry(self.searchBoxFrame, textvariable = self.searchFieldVar)
		self.listBox = Listbox(self.listBoxFrame, height = 20, width = 35)
		self.scrollBar = Scrollbar(self.listBoxFrame)

		self.searchBoxFrame.pack(side = TOP)
		self.listBoxFrame.pack(side = LEFT)
		self.btn1.pack(side = TOP, fill = X)
		self.btn2.pack(side = TOP, fill = X)
		self.btn3.pack(side = BOTTOM, fill = X)
		self.btn4.pack(side = TOP, fill = X)
		self.btn5.pack(side = LEFT, fill = X, padx = 5)
		self.inptField.pack(side = LEFT)
		self.scrollBar.pack(side = RIGHT, fill = Y)
		self.scrollBar.configure(command = self.listBox.yview)
		self.listBox.pack(side = TOP)
		self.listBox.configure(yscrollcommand = self.scrollBar.set)

		self.window.mainloop()

	def quit(self):
		self.window.destroy()

	def getListBoxData(self, data):
		self.devicesData = data
		self.listBox.delete(0, END)
		for i in self.devicesData:
			self.listBox.insert(END, i[:3])


class addNewRecordWindow(mainWindow):

	def __init__(self, parentWindow, database):
		self.parentWindow = parentWindow
		self.window = Toplevel(parentWindow)
		self.leftFrame = Frame(self.window)
		self.rightFrame = Frame(self.window)
		self.bottomFrame = Frame(self.window)
		self.inputFieldVars = []
		self.db = database

		self.bottomFrame.pack(side = BOTTOM)
		self.leftFrame.pack(side = LEFT)
		self.rightFrame.pack(side = RIGHT)

		self.labels = [
		'inventoryID',
		'deviceName',
		'osVer',
		'resolution',
		'resolutionWithoutNB',
		'aspectRatio',
		'hardwareKeyTest',
		'deviceInfoAndroid',
		'wiredTvOut',
		'miracast',
		'chromecast',
		'comment',
		'macAddress',
		'knownIssue'
		]

		for i in self.labels:
			self.label = Label(self.window, text = i)
			self.label.pack()

		for j in range(len(self.labels)):
			strVar = StringVar()
			inputField = Entry(self.rightFrame, textvariable = strVar)
			inputField.pack(pady = 1)
			self.inputFieldVars.append(strVar)

		self.addNewRecordButton = Button(self.bottomFrame, text = 'Add new record', command = self.createNewRecord)
		self.addNewRecordButton.pack(fill = X)

	def createNewRecord(self):
		patternsDic = {}
		deviceSpecsDic = {}
		for i in self.db.getPatterns():
			patternsDic[i[0]] = i[1]

		for i, j in zip(self.labels, self.inputFieldVars):
			if i in patternsDic:
				deviceSpecsDic[i] = j.get()
			else:
				continue

		if self.validate(patternsDic, deviceSpecsDic):
			self.db.addRecord('devices', [i.get() for i in self.inputFieldVars])
			self.window.destroy()


	def validate(self, patternsDic, deviceSpecsDic):
		for (i, j), (k, l) in zip(deviceSpecsDic.items(), patternsDic.items()):
			if re.match(l, j):
				pass
			else:
				return False
				break
			return True

class databaseHandler():

	def __init__(self):
		self.database = self.connectToDb()
		self.cur = self.database.cursor()
		self.patterns = self.getPatterns()

	def connectToDb(self):
		db = sql.connect(r'\\192.168.64.200\byd-fileserver\MHO\devices.db')
		return db

	def createTable(self):
		self.cur.execute("""
			CREATE TABLE IF NOT EXISTS devices (
			tester TEXT, 
			inventoryID INTEGER, 
			deviceName TEXT, 
			osVer REAL, 
			resolution TEXT, 
			resolutionWithoutNB TEXT,
			aspectRatio TEXT,
			hardwareKeyTest TEXT,
			deviceInfoAndroid TEXT,
			wiredTvOut TEXT,
			miracast TEXT,
			chromecast TEXT,
			comment TEXT,
			macAddress TEXT,
			knownIssue TEXT)
			""")
		self.database.commit()

	def viewDatabase(self):
		self.cur.execute("SELECT * FROM devices")
		data = self.cur.fetchall()
		return data

	def addRecord(self, table, data):
		if table == 'devices':
			self.cur.execute("INSERT INTO devices VALUES (None, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
		elif table == 'newPattern':
			self.cur.execute("INSERT INTO patterns VALUES (?, ?)", data)
		self.database.commit()

	def updateRecord(self, table, newPattern, cond):
		if table == 'patterns':
			self.cur.execute("UPDATE patterns SET pattern = ? WHERE record = ?", (newPattern, cond))
		elif table == 'devices':
			pass ## TO DO
		self.database.commit()

	def getPatterns(self):
		self.cur.execute("SELECT * FROM patterns")
		data = self.cur.fetchall()
		return data

if __name__ == '__main__':	
	mainWindow()
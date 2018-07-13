from tkinter import *
import sqlite3 as sql
import re

class MainWindow:

	def __init__(self):

		self.devicesData = []
		self.window = Tk()
		self.listBoxFrame = Frame(self.window)
		self.searchBoxFrame = Frame(self.window)
		self.searchFieldVar = StringVar()
		self.database = DatabaseHandler()
		self.selectedRecord = None
		self.labels = [
		'assignee',
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
		self.recordSelected = False

		self.btn1 = Button(self.window, text = 'createDb', command = self.database.createTables)
		self.btn2 = Button(self.window, text = 'viewDb', command = self.viewDb)
		self.btn3 = Button(self.window, text = 'Close', command = self.window.destroy, height = 3)
		self.btn4 = Button(self.window, text = 'Add Record', command = lambda: AddNewRecordWindow(self.window, self.database, self.labels))
		self.btn6 = Button(self.window, text = 'View Record', command = self.showRecordWindow)
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
		self.btn6.pack(side = TOP, fill = X)
		self.inptField.pack(side = LEFT)
		self.scrollBar.pack(side = RIGHT, fill = Y)
		self.scrollBar.configure(command = self.listBox.yview)
		self.listBox.pack(side = TOP)
		self.listBox.configure(yscrollcommand = self.scrollBar.set)
		self.listBox.bind('<<ListboxSelect>>', self.setSelectedRow)

		self.window.mainloop()

	def quit(self):
		self.window.destroy()

	def viewDb(self):
		self.devicesData = self.database.viewDatabase()
		self.listBox.delete(0, END)
		for i in self.devicesData:
			self.listBox.insert(END, i[:5])

	def setSelectedRow(self, event):
		self.selectedRecord = self.devicesData[self.listBox.curselection()[0]]
		self.recordSelected = True

	def showRecordWindow(self):
		if self.recordSelected == True:
			RecordWindow(self.window, self.labels, self.selectedRecord)
		else:
			print("nope") ## TO DO - add error popup


class AddNewRecordWindow(MainWindow):

	def __init__(self, parentWindow, database, labels):
		self.parentWindow = parentWindow
		self.window = Toplevel(parentWindow)
		self.leftFrame = Frame(self.window)
		self.rightFrame = Frame(self.window)
		self.bottomFrame = Frame(self.window)
		self.inputFieldVars = []
		self.db = database
		self.labels = labels[1:]

		self.bottomFrame.pack(side = BOTTOM)
		self.leftFrame.pack(side = LEFT)
		self.rightFrame.pack(side = RIGHT)

		for i in self.labels:
			self.label = Label(self.leftFrame, text = i)
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
				continue
			else:
				ErrorWindow(self.window, "Incorrect syntax of input\nin field {}.\ni={}\nj={}\nl={}".format(k, i, j, l))
				return False
		return True


class ErrorWindow():

	def __init__(self, parentWindow, error):
		self.window = Toplevel(parentWindow)
		self.l1 = Label(self.window, text = error)
		self.l1.pack()
		self.btn1 = Button(self.window, text = 'Close', command = self.window.destroy)
		self.btn1.pack()

class RecordWindow():

	def __init__(self, parentWindow, labels, record):
		self.window = Toplevel(parentWindow)
		self.labels = labels
		self.record = record
		self.bottomFrame = Frame(self.window)
		self.leftFrame = Frame(self.window)
		self.centerFrame = Frame(self.window)
		self.rightFrame = Frame(self.window)
		self.bottomFrame.pack(side = BOTTOM)
		self.leftFrame.pack(side = LEFT)
		self.centerFrame.pack(side = LEFT)
		self.rightFrame.pack(side = RIGHT)

		self.updateVariables = {}

		for i, j in zip(labels, record):
			l1 = Label(self.leftFrame, text = i)
			l1.pack()
			var1 = StringVar()
			l2 = Entry(self.centerFrame, textvariable = var1, state = 'readonly')
			var1.set(j)
			l2.pack(pady = 1)
			var2 = StringVar()
			l3 = Entry(self.rightFrame, textvariable = var2)
			self.updateVariables[i] = [j, var2]
			l3.pack(pady = 1)
		self.updateBtn = Button(self.bottomFrame, text = 'Update', command = self.update)
		self.updateBtn.pack()

	def update(self):
		for i, j in self.updateVariables.items():
			if j[1].get() is not '':
				print(i, j[0], j[1].get(), '\n', self.record)



class DatabaseHandler():

	def __init__(self):
		self.database = self.connectToDb()
		self.cur = self.database.cursor()
		self.createTables()
		self.patterns = self.getPatterns()

	def __del__(self):
		self.database.close()

	def connectToDb(self):
		#db = sql.connect(r'c:\users\armin\desktop\databasedev.db')
		db = sql.connect(r'\\192.168.64.200\byd-fileserver\MHO\devices.db')
		return db

	def createTables(self):
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
		self.cur.execute("CREATE TABLE IF NOT EXISTS patterns (field TEXT, pattern TEXT)")
		self.database.commit()

	def viewDatabase(self):
		self.cur.execute("SELECT * FROM devices")
		data = self.cur.fetchall()
		return data

	def addRecord(self, table, data):
		if table == 'devices':
			self.cur.execute("INSERT INTO devices VALUES ('None', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
		elif table == 'patterns':
			self.cur.execute("INSERT INTO patterns VALUES (?, ?)", data)
		self.database.commit()

	def updateRecord(self, expression, values):
		#print('##########################', expression)
		#print('######################', values)
		self.cur.execute(expression, values)
		self.database.commit()

	def getPatterns(self):
		self.cur.execute("SELECT * FROM patterns")
		data = self.cur.fetchall()
		return data

	def buildUpdateExpression(self, table, listOfChanges, listOfConditions):
		exp = "UPDATE {} SET ".format(table)
		for i in range(len(listOfChanges)):
			if i == len(listOfChanges)-1:
				exp = exp + str(listOfChanges[i]) + ' = ?'
			else:
				exp = exp + str(listOfChanges[i]) + ' = ?, '
		exp = exp + ' WHERE '
		for i in range(len(listOfConditions)):
			if i == len(listOfConditions)-1:
				exp = exp + str(listOfConditions[i]) + ' = ?'
			else:
				exp = exp + str(listOfConditions[i]) + ' = ? and '
		return exp

if __name__ == '__main__':	
	MainWindow()
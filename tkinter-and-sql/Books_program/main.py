from tkinter import *
import sqlite3 as sql

class mainWindow():

	def __init__(self):

		'''
		Initializing resources.
		'''

		self.window = Tk()
		self.searchFieldVar = StringVar()
		self.database = databaseHandler()
		
		'''
		Initializing objects.
		'''

		self.btn1 = Button(self.window, text = 'createDb', command = self.database.createTable)
		self.btn2 = Button(self.window, text = 'viewDb', command = lambda: self.getListBoxData(self.database.viewDatabase()))
		self.btn3 = Button(self.window, text = 'Close', command = self.quit)
		self.btn4 = Button(self.window, text = 'Add Record', command = self.database.addRecord)
		self.inptField = Entry(self.window, textvariable = self.searchFieldVar)
		self.listBox = Listbox(self.window, height = 6, width = 35)
		self.scrollBar = Scrollbar(self.window)

		'''
		Configuring objects.
		'''

		self.btn1.grid(row = 0, column = 0)
		self.btn2.grid(row = 0, column = 3)
		self.btn3.grid(row = 8, column = 3)
		self.btn4.grid(row = 1, column = 4)
		self.inptField.grid(row = 0, column = 1)
		self.listBox.grid(row = 3, column = 0, rowspan = 6, columnspan = 2)
		self.listBox.configure(yscrollcommand = self.scrollBar.set)
		self.scrollBar.grid(row = 3, column = 2, rowspan = 6)
		self.scrollBar.configure(command = self.listBox.yview)

		self.window.mainloop()

	def quit(self):
		self.window.destroy()

	def getListBoxData(self, data):
		self.listBox.delete(0, END)
		for i in data:
			self.listBox.insert(END, i[:3])


class subWindow(mainWindow):

	def __init__(self, parentWindow):
		self.parentWindow = parentWindow
		self.window = Toplevel(parentWindow)



class databaseHandler():

	def __init__(self):
		self.database = self.connectToDb()
		self.cur = self.database.cursor()

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

	def addRecord(self):
		self.cur.execute("""
			INSERT INTO devices VALUES (
			'MHO',
			'3333',
			'SGS8',
			'3.4.5',
			'2960x1440',
			'2880x1440',
			'18.5:9',
			'3129321093012390',
			'deviceinfo123123',
			'yes',
			'no',
			'no',
			'komentarz o s8',
			'mac addres to jakis tam',
			'brak known issues'
			)""")
		self.database.commit()


mainWindow()
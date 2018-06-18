from tkinter import *


class subWindow():
	def __init__(self, parentWindow, timesInvoked):
		self.parentWindow = parentWindow
		self.window = Toplevel(parentWindow)
		self.buttons = []
		self.timesInvoked = timesInvoked
		self.createButton(pos = (1, 2), text = "add", cmd = lambda: self.add())
		self.createButton(pos = (1, 1), text = "print", cmd = lambda: print(self.timesInvoked))
		self.createButton(pos = (3, 3), text = "dupa14")
		self.showAllButtons()

	def createButton(self, pos, text = None, cmd = None):
		localButton = Button(self.window, text = text, command = cmd)
		localButton.grid(row = pos[0], column = pos[1])

	def showAllButtons(self):
		for i in self.buttons:
			i.pack()

	def add(self):
		self.timesInvoked += 1

timesInvoked = 0

masterWindow = Tk()

b1 = Button(masterWindow, text='button', command=lambda: subWindow(masterWindow, timesInvoked))
b2 = Button(masterWindow, text='print info', command=lambda: print("dupa{}".format(timesInvoked)))
b1.pack()
b2.pack()





masterWindow.mainloop()
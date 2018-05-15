import subprocess
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames
import threading
import os

class filesContainer():
    def __init__(self):
        self.files = None

    def setFiles(self, f):
        self.files = f

    def getFiles(self):
        return self.files


def redirector(inputStr):
    textbox.insert(END, inputStr)
    textbox.see(END)

def displayNameOfFile():
    files = askopenfilenames(initialdir=os.getcwd())
    filesContainer.setFiles(files)

root = Tk()
filesContainer = filesContainer()
textbox=Text(root)
textbox.pack()
sys.stdout.write = redirector #redirecting all printed text into text frame
button1 = Button(root, text='get files', command=lambda: displayNameOfFile())
button1.pack()
button2 = Button(root, text='print files', command = lambda: print(filesContainer.getFiles()))
button2.pack()

root.mainloop()
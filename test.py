import subprocess
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames
import threading
import os


def redirector(inputStr):
    textbox.insert(END, inputStr)
    textbox.see(END)

def callToTextField(func, params):
    return lambda: func(*params)

def createThreads(amountOfProcess):
    for i in range(amountOfProcess):
        m_thread = threading.Thread(target = printStuff, args=('stuff{}'.format(i),))
        m_thread.start()

def printStuff(txt):
    print(txt)

def displayNameOfFile():
    files = askopenfilenames(initialdir=os.getcwd())
    print("typ files: {}".format(type(files)))
    for i in files:
        print(i)

root = Tk()
textbox=Text(root)
textbox.pack()
sys.stdout.write = redirector #redirecting all printed text into text frame
button1 = Button(root, text='test', command=displayNameOfFile)
button1.pack()

root.mainloop()
from tkinter import *

window=Tk()

b1 = Button(window,text="Find")
b1.grid(row=0,column=0)

e1 = Entry(window,textvariable=e1_value)
e1.grid(row=0,column=1)

t1 = Text(window,height=1,width=20)
t1.grid(row=0,column=2)
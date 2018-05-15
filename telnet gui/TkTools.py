from tkinter import *
from tkinter import ttk

""" http://stackoverflow.com/questions/3781670/how-to-highlight-text-in-a-tkinter-text-widget """
class CustomText(Text):# {{{

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

    def highlightPattern(self, pattern, tag, start="1.0", end="end", regexp=True):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit", count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")
# }}}

def buildOutputFrame(parent):# {{{
    outputFrame = ttk.Frame(parent)
    outputFrame.pack(side=TOP, fill=BOTH, expand=True)

    outputText = CustomText(outputFrame)

    xScrollbar = Scrollbar(outputFrame, orient=HORIZONTAL)
    xScrollbar.config(command=outputText.xview)
    xScrollbar.pack(side=BOTTOM, fill=X)

    yScrollbar = Scrollbar(outputFrame)
    yScrollbar.config(command=outputText.yview)
    yScrollbar.pack(side=RIGHT, fill=Y)

    outputText.config(xscrollcommand=xScrollbar.set, yscrollcommand=yScrollbar.set)

    return (outputFrame, outputText)
# }}}

def buildMenuFrame(content, parent, title=""):# {{{
    listboxTitle = Label(parent, text=title, bg="grey", fg="white")
    listboxTitle.pack(side=TOP, padx=5, pady=5, fill=X)

    var = StringVar(parent)
    var.set(content[0])

    menu = OptionMenu(parent, var, *content)
    menu.pack()

    return menu
# }}}

def buildListboxFrame(content, parent, title=""):# {{{
    listboxFrame = ttk.Frame(parent)
    listboxFrame.pack(side=TOP, fill=BOTH, expand=True)
    listbox = Listbox(listboxFrame, height=4)
    listbox.pack()

    listboxTitle = Label(listboxFrame, text=title, bg="grey", fg="white")
    listboxTitle.pack(side=TOP, padx=5, pady=5, fill=X)

    scrollbar = Scrollbar(listboxFrame)
    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar.config(command=listbox.yview)

    for i, line in enumerate(content):
        listbox.insert(i, line)

    listbox.config(yscrollcommand=scrollbar.set)

    return listbox
# }}}

def buildOptionLabel(parent, key, description, value=""):# {{{
    labelFrame = ttk.Labelframe(parent, text=description)
    labelFrame.pack(side=TOP, fill=X)

    inputEntry = Entry(labelFrame)
    inputEntry.insert(0, value)
    inputEntry.pack(fill=X, expand=True)

    return (key, (labelFrame, inputEntry))
# }}}

def fillListbox(listbox, content):# {{{
    listbox.delete(0, listbox.size())

    for i, line in enumerate(content):
        listbox.insert(i, line)
# }}}

def buildLabeledListbox(parent, title, buttonsFrameFunction=None):#{{{
    frame = ttk.Frame(parent)
    frame.pack(fill=BOTH, expand=True)
    listbox = Listbox(frame)
    listboxTitle = Label(frame, text=title, bg="grey", fg="white")
    listboxTitle.pack(side=TOP, padx=5, pady=5, fill=X)

    if buttonsFrameFunction:
        buttonsFrameFunction(frame)

    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar.config(command=listbox.yview)

    listbox.config(yscrollcommand=scrollbar.set)
    listbox.pack(fill=BOTH, expand=True)

    return (listbox, frame, listboxTitle)
# }}}

def buildListbox(parent, panelSide, title="", buttonsFrameFunction=None):# {{{
    listboxFrame = ttk.Frame(parent)
    listboxFrame.pack(side=panelSide, fill=BOTH)
    (listbox, frame, listboxTitle) = buildLabeledListbox(listboxFrame, title, buttonsFrameFunction)

    return (listbox, listboxFrame, listboxTitle)
# }}}

def getListboxValues(listbox):
    return [listbox.get(i) for i in range(listbox.size())]

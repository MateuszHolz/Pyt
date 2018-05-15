#!/usr/bin/python3

from collections import OrderedDict

from tkinter import *
from tkinter import ttk

from TelnetGuiConfig import *
from CmdWidgetFrame import *
from CmdEvalWidgetFrame import *


""" Notebook for CmdWidget frames objects.
"""
class CmdWidgetsFrame(ttk.Frame):
    # (type, class)
    types = {
        "0" : CmdWidgetFrame,
        "1" : CmdEvalWidgetFrame
    }

    """
    @param parent 
        Parent of this widget (ttk.Frame).
    @param rootFrame
        TelnetGui object.
    """
    def __init__(self, **kwargs):
        self.__dict__.update( kwargs )

        ttk.Frame.__init__(self, self.parent)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True)

        for name, section in self.cmdWidgetSections.items():
            typeOfWidget = section["type"]
            typeClass = self.types[typeOfWidget]
            widget = typeClass(parent=self.notebook, section=section, rootFrame=self.rootFrame)
            self.notebook.add(widget, text=section["name"])

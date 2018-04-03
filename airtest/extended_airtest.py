import os

from airtest.core.api import *
from airtest.core.device import *

class posContainer():
    def __init__(self, screenRes):
        self.container = {}
        self.screenRes = screenRes

    def addToContainer(self, positions, file):
        self.container['{}'.format(file)] = '{}x{}'.format(positions[0], positions[1])

    def getPosContainer(self):
        return self.container

def constructTemplate(file, test_section = None):
    return Template(r"{}\testsc\{}\{}".format(os.getcwd(), test_section, file))

def _waitAndTouch(file, test_section, savePos = False, posCont = None):
    localPos = wait(constructTemplate(file, test_section), interval = 1, timeout = 60)
    touch(localPos, duration = 0.2)
    if(savePos):        
        posCont.addToContainer(localPos, file)
    sleep(1)
    return

def _swipe(startPoint, endPoint, option, test_section):
    if option == "files":
        swipe(v1 = constructTemplate(startPoint, test_section), v2 = constructTemplate(endPoint, test_section), duration = 2)
    elif option == "points":
        swipe(v1 = startPoint, v2 = endPoint)

def _takeScrnShot(filename, screenRes):
    snapshot(r"{}\output\{}-{}".format(os.getcwd(), screenRes, filename))
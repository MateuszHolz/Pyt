import os
from airtest.core.api import *
from airtest.core.device import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import re
import subprocess

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
    sleep(4)

def _swipe(startPoint, endPoint, option, test_section):
    if option == "files":
        swipe(v1 = constructTemplate(startPoint, test_section), v2 = constructTemplate(endPoint, test_section), duration = 5)
    elif option == "points":
        swipe(v1 = startPoint, v2 = endPoint)

def _takeScrnShot(filename, screenRes = False):
    if screenRes:
        fileDir = r"{}\output\{}-{}.png".format(os.getcwd(), screenRes, filename)
    else:
        fileDir = r"{}\output\{}.png".format(os.getcwd(), filename)
    snapshot(fileDir)
    return fileDir

def getErrorImage():
    errorImg = _takeScrnShot("error")
    with open(errorImg, 'rb') as f:
        _attachment = MIMEImage(f.read())
    return _attachment

def getLogcat(dir, serialNo):
    with open(dir, 'w', encoding='utf-8') as f:
        f.write(subprocess.check_output(r'adb -s {} logcat -d'.format(serialNo)).decode('utf-8', errors='backslashreplace'))
    return dir


def sendMail(auth, takeImage = None, serialNo = None, bodyTxt = None, subject = None):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(auth[0], auth[1])
    msg = MIMEMultipart()
    if bodyTxt:
        msgText = MIMEText(bodyTxt)
        msg.attach(msgText)
    if takeImage:
        msg.attach(getErrorImage())
    if serialNo:
        with open(getLogcat('logcat.txt', serialNo), encoding='utf-8') as f:
            logcat = MIMEApplication(f.read())
        logcat['Content-Disposition'] = 'attachment; filename="logcat.txt"'
        msg.attach(logcat)
    if subject:
        msg['Subject'] = subject
    server.sendmail(auth[0], "mateusz.holz@huuugegames.com", msg.as_string())
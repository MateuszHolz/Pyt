import os
from airtest.core.api import *
from airtest.core.device import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import re
import time
import subprocess
import json

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

def sendMail(jsonData):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("testergamelion66@gmail.com", "dupa1212")
    msg = MIMEMultipart()
    #TEXT#
    msgText = MIMEText(jsonData['Error_txt'])
    msg.attach(msgText)
    #IMG#
    msg.attach(getErrorImage(jsonData['Error_img']))
    #LOGCAT#
    logcatAttachment = MIMEApplication(open(jsonData['Logcat'], 'rb').read())
    logcatAttachment['Content-Disposition'] = 'attachment; filename="logcat.txt"'
    msg.attach(logcatAttachment)
    msg['Subject'] = 'Test failed.'
    server.sendmail("testergamelion66@gmail.com", "mateusz.holz@huuugegames.com", msg.as_string())


def _waitAndTouch(file, test_section, savePos = False, posCont = None):
    try:
        localPos = wait(constructTemplate(file, test_section), interval = 1, timeout = 2)
        touch(localPos, duration = 0.2)
        if(savePos):        
            posCont.addToContainer(localPos, file)
        sleep(4)
    except Exception as err:
        errDict = {}
        errDict['Error_txt'] = str(err)
        errDict['Error_img'] = _takeScrnShot('error')
        errDict['Logcat'] = getLogcat("{}\logcat.txt".format(os.getcwd()), getSerialNo())
        print('\n\n\n error(inside script): \n {} \n\n\n'.format(str(err)))
        with open('error.json', 'w') as f:
            f.write(json.dumps(errDict))
        print(errDict)
        return 1

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

def getErrorImage(errorImg):
    attachment = open(errorImg, 'rb')
    _attachment = MIMEImage(attachment.read())
    attachment.close()
    return _attachment

def getLogcat(dir, serialNo):
    with open(dir, 'w', encoding='utf-8') as f:
        f.write(subprocess.check_output(r'adb -s {} logcat -d'.format(serialNo)).decode('utf-8', errors='ignore'))
    return dir

def getSerialNo():
    return device().getprop("ro.serialno")
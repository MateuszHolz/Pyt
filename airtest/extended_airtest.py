import os
from airtest.core.api import *
from airtest.core.device import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import subprocess

class airtestAutomation():
    def __init__(self, devId, packageName, runApp = None, clearData = None):
        self.devId = devId
        self.packageName = packageName
        self.testSection = None
        self.device = self.connectToDevice()
        self.index = 0
        if clearData:
            self.clearAppData()
        if runApp:
            self.runApp()

    def connectToDevice(self):
        try:
            device = connect_device('android:///{}'.format(self.devId))
        except Exception:
            device = connect_device('android:///{}'.format(self.devId))
        wake()
        return device

    def clearAppData(self, optionalPckName = None):
        if optionalPckName:
            clear_app(optionalPckName)
        else:
            clear_app(self.packageName)

    def runApp(self):
        start_app(self.packageName)

    def setTestSection(self, testSection):
        self.testSection = testSection

    def waitAndTouch(self, file, sleepTime = 4, timeout = 60):
        localPos = wait(self.constructTemplate(file), interval = 1, timeout = 60)
        touch(localPos, duration = 0.2)
        sleep(sleepTime)

    def constructTemplate(self, file):
        return Template(r"{}\testsc\{}\{}.png".format(os.getcwd(), self.testSection, file))

    def swipe(self, startPoint, endPoint, option):
        if option == "files":
            swipe(v1 = self.constructTemplate(startPoint), v2 = self.constructTemplate(endPoint), duration = 5)
        elif option == "points":
            swipe(v1 = startPoint, v2 = endPoint)

    def takeScreenShot(self, filename):
        fileDir = r"{}\output\{}.png".format(os.getcwd(), filename)
        snapshot(fileDir)
        return fileDir

    def getErrorImage(self):
        errorImg = self.takeScreenShot("error")
        with open(errorImg, 'rb') as f:
            _attachment = MIMEImage(f.read())
        return _attachment

    def getLogcat(self, dir):
        with open(dir, 'w', encoding='utf-8') as f:
            f.write(subprocess.check_output(r'adb -s {} logcat -d'.format(self.devId)).decode('utf-8', errors='backslashreplace'))
        return dir

    def sendMail(self, auth, takeImage = None, getLogcat = None, bodyTxt = None, subject = None):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(auth[0], auth[1])
        msg = MIMEMultipart()
        if bodyTxt:
            msgText = MIMEText(bodyTxt)
            msg.attach(msgText)
        if takeImage:
            msg.attach(self.getErrorImage())
        if getLogcat:
            with open(self.getLogcat('logcat.txt'), encoding='utf-8') as f:
                logcat = MIMEApplication(f.read())
            logcat['Content-Disposition'] = 'attachment; filename="logcat.txt"'
            msg.attach(logcat)
        if subject:
            msg['Subject'] = subject
        server.sendmail(auth[0], "mateusz.holz@huuugegames.com", msg.as_string())
        
    def runShellCommand(self, cmd):
        shell(cmd)

    def type(self, txt):
        text(txt)

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

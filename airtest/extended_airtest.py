import os
from airtest.core.api import *
from airtest.core.device import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import subprocess
import telnetlib
from datetime import datetime

class airtestAutomation():
    def __init__(self, devId, packageName, runApp = None, clearData = None):
        self.devId = devId
        self.packageName = packageName
        self.testSection = None
        self.device = self.connectToDevice()
        self.index = 0
        self.telnetClient = None
        self.currentScreen = None
        self.currentAction = None
        self.templatesDict = {}
        self.auth = ('testergamelion66@gmail.com', 'dupa1212')
        if clearData: self.clearAppData()
        if runApp: self.runApp()

    def getCurrentTimestamp(self):
        return datetime.timestamp(datetime.now())

    def createTelnetClient(self):
        self.setCurrAction('createTelnetClient')
        self.setCurrScreen(None)
        self.telnetClient = telnetlib.Telnet(self.getDeviceIpAddr(), '1337')

    def closeTelnetClient(self):
        self.setCurrAction('closeTelnetClient')
        self.setCurrScreen(None)
        self.telnetClient.close()
        self.telnetClient = None

    def connectToDevice(self):
        self.setCurrAction('connectToDevice')
        self.setCurrScreen(None)
        try:
            device = connect_device('android:///{}'.format(self.devId))
        except Exception:
            device = connect_device('android:///{}'.format(self.devId))
        wake()
        return device

    def clearAppData(self, optionalPckName = None):
        clear_app(optionalPckName) if optionalPckName else clear_app(self.packageName)

    def runApp(self):
        self.setCurrAction('runApp')
        self.setCurrScreen(None)
        start_app(self.packageName)

    def setTestSection(self, testSection):
        self.setCurrAction('setTestSection')
        self.setCurrScreen(None)
        self.testSection = testSection

    def getTestSection(self):
        self.setCurrAction('getTestSection')
        self.setCurrScreen(None)
        return self.testSection

    def waitAndTouch(self, file, sleepTime = 4, timeout = 60, interval = 1, duration = 0.2):
        temp = self.constructTemplate(file)
        self.setCurrAction('waitAndTouch')
        self.setCurrScreen(file)
        localPos = wait(temp, interval = interval, timeout = timeout)
        touch(localPos, duration = duration)
        sleep(sleepTime)

    def constructTemplate(self, file):
        self.setCurrAction('constructTemplate')
        self.setCurrScreen(file)
        if file in self.templatesDict:
            return self.templatesDict[file]
        else:
            temp = Template(r"{}\testsc\{}\{}.png".format(os.getcwd(), self.testSection, file))
            self.templatesDict[file] = temp
            return temp

    def setCurrScreen(self, currentScreen):
        self.currentScreen = currentScreen

    def getCurrScreen(self):
        return self.currentScreen

    def setCurrAction(self, currentAction):
        self.currentAction = currentAction

    def getCurrAction(self):
        return self.currentAction

    def swipe(self, startPoint, endPoint, option, duration = 5):
        self.setCurrAction('swipe')
        self.setCurrScreen((startPoint, endPoint))
        if option == "files":
            temp1 = self.constructTemplate(startPoint)
            temp2 = self.constructTemplate(endPoint)
            swipe(v1 = temp1, v2 = temp2, duration = duration)
        elif option == "points": swipe(v1 = startPoint, v2 = endPoint, duration = duration)
    
    def swipeToDirection(self, direction, power):
        '''
        power(s):
        - low
        - mid
        - high
        Throws exception when power any other than that has been provided. 
        '''
        deviceRes = self.getDeviceSize()
        if direction == 'left':
            self.swipe(startPoint = (0.75 * deviceRes[0], 0.5 * deviceRes[1]), endPoint = (0.25 * deviceRes[0], 0.5 * deviceRes[1]), option = 'points', duration = 1)
        elif direction == 'right':
            self.swipe(startPoint = (0.25 * deviceRes[0], 0.5 * deviceRes[1]), endPoint = (0.75 * deviceRes[0], 0.5 * deviceRes[1]), option = 'points', duration = 1)
        elif direction == 'up':
            self.swipe(startPoint = (0.5 * deviceRes[0], 0.75 * deviceRes[1]), endPoint = (0.5 * deviceRes[0], 0.25 * deviceRes[1]), option = 'points', duration = 1)
        elif direction == 'down':
            self.swipe(startPoint = (0.5 * deviceRes[0], 0.25 * deviceRes[1]), endPoint = (0.5 * deviceRes[0], 0.75 * deviceRes[1]), option = 'points', duration = 1)
        else:
            raise TypeError('ACTION "{}" NOT IMPLEMENTED'.format(direction))

    def takeScreenShot(self, filename):
        self.setCurrAction('takeScreenShot')
        self.setCurrScreen(None)
        fileDir = r"{}\output\{}.png".format(os.getcwd(), filename)
        snapshot(fileDir)
        return fileDir

    def getDeviceSize(self):
        raw = self.runShellCommand('wm size').split()[2]
        raw = raw.replace('x', ' ').split()
        return float(raw[1]), float(raw[0])

    def getErrorImage(self):
        self.setCurrAction('getErrorImage')
        self.setCurrScreen(None)
        errorImg = self.takeScreenShot("error")
        with open(errorImg, 'rb') as f:
            _attachment = MIMEImage(f.read())
        return _attachment

    def getLogcat(self, dir):
        data = self.runShellCommand('logcat -d')
        self.setCurrAction('getLogcat')
        self.setCurrScreen(None)
        with open(dir, 'w', encoding='utf-8') as f:
            f.write(data)
        return dir


    def sendMail(self, takeImage = None, getLogcat = None, bodyTxt = None, subject = None):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.auth[0], self.auth[1])
        msg = MIMEMultipart()
        if bodyTxt:
            msgText = MIMEText(bodyTxt)
            msg.attach(msgText)
        if takeImage: msg.attach(self.getErrorImage())
        if getLogcat:
            with open(self.getLogcat('logcat.txt'), encoding='utf-8') as f:
                logcat = MIMEApplication(f.read())
            logcat['Content-Disposition'] = 'attachment; filename="logcat.txt"'
            msg.attach(logcat)
        if subject: msg['Subject'] = subject
        server.sendmail(self.auth[0], "mateusz.holz@huuugegames.com", msg.as_string())
        
    def runShellCommand(self, cmd):
        self.setCurrAction('runShellCommand')
        self.setCurrScreen(None)
        return shell(cmd)

    def type(self, txt):
        self.setCurrAction('type')
        self.setCurrScreen(None)
        text(txt)
        sleep(2)

    def deleteChar(self, times = 1):
        self.setCurrAction('deleteText')
        self.setCurrScreen(None)
        for i in range(times):
            shell('input keyevent 67')

    def setIndex(self, index):
        self.setCurrAction('setIndex')
        self.setCurrScreen(None)
        self.index = index

    def getIndex(self, mail = False):
        if mail == False:
            self.setCurrAction('getIndex')
            self.setCurrScreen(None)
        return self.index

    def wait(self, time):
        self.setCurrAction('wait')
        self.setCurrScreen(None)
        sleep(time)

    def getDeviceIpAddr(self):
        self.setCurrAction('getDeviceIpAddr')
        self.setCurrScreen(None)
        output = self.runShellCommand('ip -f inet addr show wlan0')
        ipAddr = output[output.index('inet')+5:output.index('/')]
        return ipAddr

    def runTelnetCommand(self, cmd):
        self.setCurrAction('runTelnetCommand')
        self.setCurrScreen(None)
        self.createTelnetClient()
        self.telnetClient.write(cmd.encode('ascii')+b'\r\n')
        self.closeTelnetClient()

    def returnCoordinatesIfExist(self, file):
        temp = self.constructTemplate(file)
        self.setCurrAction('returnCoordinatesIfExist')
        self.setCurrScreen(file)
        return exists(temp)

    def useDeviceBackButton(self, sleepTime = 4):
        self.setCurrAction('useDeviceBackButton')
        self.setCurrScreen(None)
        self.runShellCommand('input keyevent 4')
        sleep(sleepTime)
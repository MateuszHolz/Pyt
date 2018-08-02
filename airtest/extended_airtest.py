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
        self.predefinedTelnetCommands = {
            #'getChips': self.getChips
            # TO DO - create list of predefined telnet functions that return desired 
            # values and implement their corresponding functions.
        }
        if clearData: self.clearAppData()
        if runApp: self.runApp()

    def getCurrentTimestamp(self, data):
        return datetime.timestamp(datetime.now())

    def createTelnetClient(self):
        self.setCurrAction('createTelnetClient')
        self.setCurrScreen(None)
        if not self.telnetClient:
            self.telnetClient = telnetlib.Telnet(self.getDeviceIpAddr(), '1337')
            return self.fetchDataUntilNewLine()
        else:
            raise Exception('Telnet client was already created before.')

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
    
    def swipeToDirection(self, direction, power, duration = 1):
        '''
        power(s):
        - low
        - mid
        - high
        Throws exception when power any other than that has been provided. Accepts only string.

        direction(s):
        - left
        - right
        - up
        - down
        Throws exception when direction any other than that has been provided. Accepts only string.
        '''
        low = (0.55, 0.45)
        mid = (0.65, 0.35)
        high = (0.75, 0.25)
        usedParams = None
        if not isinstance(direction, str) or not isinstance(power, str):
            raise TypeError('Parameters direction and power must be str!')
        deviceRes = self.getDeviceSize()
        if power == 'low':
            usedParams = low
        elif power == 'mid':
            usedParams = mid
        elif power == 'high':
            usedParams = high
        else:
            raise TypeError('Incorect option chosen for parameter power: {}. Available options: "low", "mid", "high".')
        if direction == 'left':
            self.swipe(startPoint = (usedParams[0] * deviceRes[0], 0.5 * deviceRes[1]), endPoint = (usedParams[1] * deviceRes[0], 0.5 * deviceRes[1]), option = 'points', duration = duration)
        elif direction == 'right':
            self.swipe(startPoint = (usedParams[1] * deviceRes[0], 0.5 * deviceRes[1]), endPoint = (usedParams[0] * deviceRes[0], 0.5 * deviceRes[1]), option = 'points', duration = duration)
        elif direction == 'up':
            self.swipe(startPoint = (0.5 * deviceRes[0], usedParams[0] * deviceRes[1]), endPoint = (0.5 * deviceRes[0], usedParams[1] * deviceRes[1]), option = 'points', duration = duration)
        elif direction == 'down':
            self.swipe(startPoint = (0.5 * deviceRes[0], usedParams[1] * deviceRes[1]), endPoint = (0.5 * deviceRes[0], usedParams[0] * deviceRes[1]), option = 'points', duration = duration)
        else:
            raise TypeError('Incorect option chosen for parameter direction: {}. Available options: "left", "right", "up", "down".'.format(direction))

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
        print(ipAddr)
        return ipAddr

    def sendTelnetCommand(self, cmd = None, type = None):
        self.setCurrAction('runTelnetCommand')
        self.setCurrScreen(None)
        if self.telnetClient:
            if not type:
                self.telnetClient.write(cmd.encode('ascii')+b'\r\n')
                return self.fetchDataUntilNewLine()
            else:
                if not cmd:
                    self.predefinedTelnetCommands[type]()
                else:
                    raise Exception('You can use only 1 param at once.')
        else:
            raise Exception('Telnet connection is not established. Create telnet client to fix this problem.')

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
    
    def fetchDataUntilNewLine(self):
        receivedLine = "_"
        data = []
        endOfContentStr = b'\n'
        isAvailableData = lambda data: data and data != b'' and data != endOfContentStr

        while isAvailableData(receivedLine):
            receivedLine = self.telnetClient.read_until(endOfContentStr, 1)
            data.append(receivedLine.rstrip().decode("utf-8"))

        return data

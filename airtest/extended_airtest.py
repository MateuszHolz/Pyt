import os
import smtplib
import subprocess
import telnetlib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from airtest.core.api import *
from airtest.core.device import *


class airtestAutomation():
    def __init__(self, devId, packageName, setup = True, ip = None, runApp = None, clearData = None):
        self.ipAddress = ip
        self.lobbyPopups = ('mystery_reward_continue', 'bucks_unlocked')
        self.devId = devId
        self.packageName = packageName
        self.testSection = None
        self.device = self.connectToDevice()
        self.index = 0
        self.telnet = None
        self.currentScreen = None
        self.currentAction = None
        self.templatesDict = {}
        if clearData: self.clearAppData()
        if runApp: self.runApp()
        if setup: self.standardSetup()
    
    def standardSetup(self):
        self.clearAppData()
        self.runApp()
        self.type('ad')
        self.wait(2)
        self.runShellCommand('logcat -c')
    
    def createTelnet(self, automat):
        if not self.telnet:
            self.telnet = Telnet(automat)
        else:
            print('Telnet client is already initalized.')

    def closeTelnet(self):
        if self.telnet:
            self.telnet.close()
            self.telnet = None
        else:
            print('Telnet client was already closed / never existed.')

    def getCurrentTimestamp(self):
        self.setLatestInfo('getCurrentTimestamp', None)
        return datetime.timestamp(datetime.now())

    def connectToDevice(self):
        self.setLatestInfo('connectToDevice', None)
        if self.ipAddress is not None:
            retries = 0
            while True:
                try:
                    device = connect_device('android://{}:{}/{}'.format(self.ipAddress, '5555', self.devId))
                    break
                except Exception:
                    if retries > 3:
                        raise Exception('Max amount of retries for connecting to device with ip: {} reached!'.format(retries))
                    retries += 1
                    continue
        else:
            retries = 0
            while True:
                try:
                    device = connect_device('android:///{}'.format(self.devId))
                    break
                except Exception:
                    if retries > 3:
                        raise Exception('Max amount of retries via cable: {} reached!'.format(retries))
                    retries += 1
                    continue
        wake()
        return device

    def clearAppData(self, optionalPckName = None):
        self.setLatestInfo('clearAppData', None)
        clear_app(optionalPckName) if optionalPckName else clear_app(self.packageName)

    def runApp(self):
        self.setLatestInfo('runApp', None)
        start_app(self.packageName)

    def setTestSection(self, testSection):
        self.setLatestInfo('setTestSection', None)
        self.testSection = testSection

    def getTestSection(self):
        self.setLatestInfo('getTestSection', None)
        return self.testSection

    def waitAndTouch(self, file, sleepTime = 4, timeout = 60, interval = 1, duration = 0.2):
        temp = self.constructTemplate(file)
        self.setLatestInfo('waitAndTouch', file)
        localPos = wait(temp, interval = interval, timeout = timeout)
        touch(localPos, duration = duration)
        sleep(sleepTime)

    def swipeRightUntil(self, file):
        temp = self.constructTemplate(file)
        self.setLatestInfo('swipeRightUntil', file)
        tries = 0
        while True:
            if tries > 15:
                raise Exception('Maximum amount of tries ({}) reached!'.format(tries))
            tries += 1
            if exists(temp):
                self.swipeToDirection(direction = 'right', power = 'low', duration = 0.5)
                break
            else:
                self.swipeToDirection(direction = 'right', power = 'mid', duration = 0.5)

    def constructTemplate(self, file):
        self.setLatestInfo(curAc = 'constructTemplate', curSc = file)
        if file in self.templatesDict:
            return self.templatesDict[file]
        else:
            temp = Template(r"{}\testsc\{}\{}.png".format(os.getcwd(), self.testSection, file))
            self.templatesDict[file] = temp
            return temp

    def setLatestInfo(self, curAc = None, curSc = None):
        self.currentAction = curAc
        self.currentScreen = curSc

    def getLatestActions(self):
        return self.currentAction, self.currentScreen

    def swipe(self, startPoint, endPoint, option, duration = 5):
        self.setLatestInfo(curAc = 'swipe', curSc = (startPoint, endPoint))
        if option == "files":
            temp1 = self.constructTemplate(startPoint)
            temp2 = self.constructTemplate(endPoint)
            swipe(v1 = temp1, v2 = temp2, duration = duration)
        elif option == "points": swipe(v1 = startPoint, v2 = endPoint, duration = duration)
    
    def swipeToDirection(self, direction, power, duration = 3):
        '''
        direction(s):
        - left
        - right
        - up
        - down
        Throws exception when direction any other than that has been provided. Accepts only string.
        
        power(s):
        - low
        - mid
        - high
        Throws exception when power any other than that has been provided. Accepts only string.
        '''
        self.setLatestInfo('swipeToDirection', self.getLatestActions()[1])
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
            raise TypeError('Incorect option chosen for parameter power: {}. Available options: "low", "mid", "high".'.format(power))
        if direction == 'right':
            self.swipe(startPoint = (usedParams[0] * deviceRes[0], 0.5 * deviceRes[1]), endPoint = (usedParams[1] * deviceRes[0], 0.5 * deviceRes[1]), option = 'points', duration = duration)
        elif direction == 'left':
            self.swipe(startPoint = (usedParams[1] * deviceRes[0], 0.5 * deviceRes[1]), endPoint = (usedParams[0] * deviceRes[0], 0.5 * deviceRes[1]), option = 'points', duration = duration)
        elif direction == 'up':
            self.swipe(startPoint = (0.5 * deviceRes[0], usedParams[0] * deviceRes[1]), endPoint = (0.5 * deviceRes[0], usedParams[1] * deviceRes[1]), option = 'points', duration = duration)
        elif direction == 'down':
            self.swipe(startPoint = (0.5 * deviceRes[0], usedParams[1] * deviceRes[1]), endPoint = (0.5 * deviceRes[0], usedParams[0] * deviceRes[1]), option = 'points', duration = duration)
        else:
            raise TypeError('Incorect option chosen for parameter direction: {}. Available options: "left", "right", "up", "down".'.format(direction))

    def takeScreenShot(self, filename):
        self.setLatestInfo('takeScreenShot', None)
        fileDir = r"{}\output\{}.png".format(os.getcwd(), filename)
        snapshot(fileDir)
        return fileDir

    def getDeviceSize(self):
        self.setLatestInfo('getDeviceSize', None)
        raw = self.runShellCommand('wm size').split()[2]
        raw = raw.replace('x', ' ').split()
        return float(raw[1]), float(raw[0])

    def getErrorImage(self):
        self.setLatestInfo('getErrorImage', None)
        errorImg = self.takeScreenShot("error")
        with open(errorImg, 'rb') as f:
            _attachment = MIMEImage(f.read())
        return _attachment

    def getLogcat(self, dir):
        data = self.runShellCommand('logcat -d')
        self.setLatestInfo('getLogcat', None)
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
        self.setLatestInfo('sendMail', None)
        server.sendmail(self.auth[0], "mateusz.holz@huuugegames.com", msg.as_string())
        
    def runShellCommand(self, cmd):
        self.setLatestInfo('runShellCommand', None)
        return shell(cmd)

    def type(self, txt):
        self.setLatestInfo('type', None)
        text(txt)
        sleep(2)

    def deleteChar(self, times = 1):
        self.setLatestInfo('deleteChar', None)
        for i in range(times):
            shell('input keyevent 67')

    def setIndex(self, index):
        self.setLatestInfo('setIndex', None)
        self.index = index

    def getIndex(self, mail = False):
        self.setLatestInfo('getIndex', None)
        return self.index

    def wait(self, time):
        self.setLatestInfo('wait', None)
        sleep(time)

    def getDeviceIpAddr(self):
        self.setLatestInfo('getDeviceIpAddr', None)
        output = self.runShellCommand('ip -f inet addr show wlan0')
        ipAddr = output[output.index('inet')+5:output.index('/')]
        return ipAddr

    def returnCoordinatesIfExist(self, file):
        temp = self.constructTemplate(file)
        self.setLatestInfo('returnCoordinatesIfExist', file)
        return exists(temp)

    def useDeviceBackButton(self, sleepTime = 4):
        self.setLatestInfo('useDeviceBackButton', None)
        self.runShellCommand('input keyevent 4')
        sleep(sleepTime)

class Telnet():
    def __init__(self, airtest):
        self.airtest = airtest
        self.airtest.setLatestInfo('Initializing Telnet object.', None)
        self.connection = telnetlib.Telnet(self.airtest.getDeviceIpAddr(), '1337')
        self.fetchData()
        
    def fetchData(self):
        self.airtest.setLatestInfo('fetchData', None)
        receivedLine = "_"
        data = []
        endOfContentStr = b'\n'
        isAvailableData = lambda data: data and data != b'' and data != endOfContentStr

        while isAvailableData(receivedLine):
            receivedLine = self.connection.read_until(endOfContentStr, 1)
            data.append(receivedLine.rstrip().decode("utf-8"))

        return data
    
    def close(self):
        self.airtest.setLatestInfo('Deleting Telnet object.', None)
        self.connection.close()

    def sendTelnetCommand(self, cmd = None):
        self.airtest.setLatestInfo('sendTelnetCommand', None)
        self.connection.write(cmd.encode('ascii')+b'\r\n')
        return self.fetchData()

    def getUserId(self):
        keyword = 'User ID'
        raw = self.sendTelnetCommand('getInfo')
        self.airtest.setLatestInfo('getUserId', None)
        userid = None
        for i in raw:
            if keyword in i:
                userid = i.split()[2]
        return userid

    def getChipsBalance(self):
        raw = self.sendTelnetCommand('server playerchange chips 0')
        self.airtest.setLatestInfo('getChipsBalance', None)
        curChips = raw[0].split()[5][:-1]
        return curChips

    def setChipsBalance(self, balance):
        while True:
            curBalance = int(self.getChipsBalance())
            if curBalance == balance: break
            self.airtest.setLatestInfo('setChipsBalance', None)
            chipsDelta = balance - curBalance
            self.sendTelnetCommand('server playerchange chips {}'.format(chipsDelta))
            self.sendTelnetCommand('disconnect')
            self.airtest.wait(5)

    def getLevel(self):
        raw = self.sendTelnetCommand('server playerchange level 0')
        self.airtest.setLatestInfo('getLevel', None)
        return int(raw[0].split()[5][:-1])

    def getSessionId(self):
        keyword = 'Session_id'
        raw = self.sendTelnetCommand('getInfo')
        self.airtest.setLatestInfo('getSessionId', None)
        for i in raw:
            if keyword in i:
                sessionid = i.split()[1]
        return sessionid

    def setNextLotteryTicketSafe(self, ticketType):
        listOfTickets = self.sendTelnetCommand('server lottery {} list'.format(ticketType))
        for i in listOfTickets:
            if 'chips' in i:
                safeIndex = i.split()[0]
        self.sendTelnetCommand('server lottery {} {}'.format(ticketType, safeIndex))

    def reachLevel(self, lvl, skipLobbyPopups = False):
        self.sendTelnetCommand('server playerchange level {}'.format(lvl - self.getLevel()))
        self.airtest.wait(2)
        self.sendTelnetCommand('disconnect')
        self.airtest.wait(5)
        self.airtest.setTestSection('utils')
        if not skipLobbyPopups:
            return 0
        else:
            while True:
                self.airtest.wait(3)
                if not self.airtest.returnCoordinatesIfExist('mystery_reward_continue'):
                    if self.airtest.returnCoordinatesIfExist('bucks_unlocked'):
                        self.airtest.waitAndTouch('bucks_unlocked')
                        self.airtest.wait(3)
                        break
                    else:
                        break
                else:
                    self.airtest.waitAndTouch('mystery_reward_continue', sleepTime = 2)
        return 0

import os
import re
import subprocess

class Adb():
    def __init__(self):
        pass

    @staticmethod
    def getOutputOfCmd(cmd, timeout = 15, outputAsList = False):
        out = None
        err = None
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        try:
            outputBytes, errorBytes = process.communicate(timeout = timeout)
            if outputAsList == True:
                out = outputBytes.decode().split()
            else:
                out = outputBytes.decode().rstrip()
            err = errorBytes.decode().rstrip()
            return out, err
        except subprocess.TimeoutExpired:
            process.kill()
            out, err = process.communicate()
            return '', 'Timed out'

    @staticmethod
    def handleErrorMsg(msg):
        if 'not found' in msg:
            return 'Device not found'
        elif 'unauthorized' in msg:
            return 'Unauthorized'
        elif 'INSTALL_FAILED_VERSION_DOWNGRADE' in msg:
            return 'Downgrade error'
        else:
            return msg

    @staticmethod
    def uninstallApp(device, pckg):
        cmd = r'adb -s {} uninstall {}'.format(device, pckg)
        _, errStr = Adb.getOutputOfCmd(cmd)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        return True, 'Success'

    @staticmethod
    def isApkDebuggable(build):
        cmd = r'aapt dump badging {}'.format(build)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in outList:
            if 'application-debuggable' in i:
                return True, 'True'
            return True, 'False'

    @staticmethod
    def deleteFile(device, fullPath):
        cmd = r'adb -s {} shell rm {}'.format(device, fullPath)
        _, errStr = Adb.getOutputOfCmd(cmd)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        return True, 'Success'

    @staticmethod
    def isInstalledPackageDebuggable(device, pckg):
        cmd = r'adb -s {} shell dumpsys package {}'.format(device, pckg)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in [j.replace(' ', '') for j in outList]:
            if 'flags' in i:
                if 'DEBUG' in i:
                    return True, 'True'
            return False, 'False'
    
    @staticmethod
    def removeLocalAppData(device, pckg):
        cmd = r'adb -s {} shell pm clear {}'.format(device, pckg)
        outStr, errStr = Adb.getOutputOfCmd(cmd)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        return True, outStr

    @staticmethod
    def isBuildIsAlreadyInstalled(device, pckg):
        cmd = r'adb -s {} shell pm list packages'.format(device)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in outList:
            if pckg in i:
                return True, 'Build exists'
        return False, 'Build doesnt exist'

    @staticmethod
    def getPackageNameOfAppFromApk(build):
        cmd = r'aapt dump badging {}'.format(build)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in outList:
            if 'com.' in i:
                return True, i[i.find('com.'):-1]

    @staticmethod
    def getBuildVersionFromApk(build):
        cmd = r'aapt dump badging {}'.format(build)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in outList:
            if 'versionName' in i:
                return True, i[i.find('=')+2:-1]

    @staticmethod
    def getListOfAttachedDevices():
        devices = []
        retries = 0
        while True:
            if retries > 4:
                break
            else:
                try:
                    _l = subprocess.check_output(r"adb devices", shell = True)
                    if "doesn't" in _l.decode():
                        retries += 1
                        continue
                    else:
                        break
                except subprocess.CalledProcessError:
                    retries += 1
                    continue
        rawList = _l.rsplit()
        tempList = rawList[4:]
        for idx, i in enumerate(tempList):
            if idx%2 == 0:
                status = tempList[idx+1].decode()
                devices.append((i.decode(), 'Authorized' if status == 'device' else 'Unauthorized'))
        return devices
    
    @staticmethod
    def captureScreenshot(device, filename):
        dirOnDevice = os.path.join('sdcard/', filename)
        cmd = r'adb -s {} shell screencap "{}"'.format(device, dirOnDevice)
        _, errStr = Adb.getOutputOfCmd(cmd)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr), ''
        else:
            return True, 'Done', dirOnDevice

    @staticmethod
    def pullScreenshot(device, fullPathOnDevice, destinationDirectory):
        cmd = r'adb -s {} pull "{}" {}'.format(device, fullPathOnDevice, destinationDirectory)
        outStr, errStr = Adb.getOutputOfCmd(cmd)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        elif 'not found' in outStr:
            return False, 'Device not found'
        else:
            return True, 'Done'

    @staticmethod
    def installBuild(device, build):
        timeout = 60
        cmd = r'adb -s {} install -r "{}"'.format(device, build)
        outStr, errStr = Adb.getOutputOfCmd(cmd, timeout)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        else:
            return True, outStr

    @staticmethod
    def getBuildVersionNameFromDevice(device, pckg):
        cmd = r'adb -s {} shell dumpsys package {}'.format(device, pckg)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in outList:
            if 'versionName' in i:
                return True, i[i.find('=')+1:]
        return False, 'Not found'

    @staticmethod
    def getBuildVersionCodeFromDevice(device, pckg):
        cmd = r'adb -s {} shell dumpsys package {}'.format(device, pckg)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in outList:
            if 'versionCode' in i:
                return True, i[i.find('=')+1:]
        return False, 'Not found'

    @staticmethod
    def getDeviceIpAddress(device):
        cmd = r"adb -s {} shell ip addr show wlan0".format(device)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for i in outList:
            if i[0:7] == '192.168':
                return True, i[0:len(i)-3]
        return True, 'Not set'

    @staticmethod
    def getDeviceScreenSize(device):
        cmd = r'adb -s {} shell wm size'.format(device)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        deviceResolution = re.sub('x', ' ', outList[2]).split()
        return True, "{}x{}".format(deviceResolution[1], deviceResolution[0])

    @staticmethod
    def getBatteryStatus(device):
        cmd = r'adb -s {} shell dumpsys battery'.format(device)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for idx, i in enumerate(outList):
            if i == 'level:':
                return True, outList[idx+1]+'%'

    @staticmethod
    def getPluggedInStatus(device):
        cmd = r'adb -s {} shell dumpsys battery'.format(device)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        for idx, i in enumerate(outList):
            if i == 'AC' or i == 'USB':
                if out[idx+2] == 'true':
                    return True, 'True, {} powered'.format(i)
            else:
                return True, 'False'

    @staticmethod
    def getWifiName(device):
        cmd = r'adb -s {} shell dumpsys wifi'.format(device)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        else:
            for idx, i in enumerate(outList):
                if i == 'mWifiInfo':
                    if outList[idx+2][1:] == 'unknown':
                        return True, 'Not set'
                    else:
                        return True, outList[idx+2][:-1]

    @staticmethod
    def getListOfInstalledPackages(device):
        packages = []
        localList = ('huuuge', 'gamelion')
        cmd = r'adb -s {} shell pm list packages'.format(device)
        outList, errStr = Adb.getOutputOfCmd(cmd, outputAsList = True)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        else:
            for package in localList:
                for line in outList:
                    if package in line:
                        packages.append(line[8:])
            return True, packages
    
    @staticmethod
    def getProperty(device, prop):
        cmd = r'adb -s {} shell getprop {}'.format(device, prop)
        outStr, errStr = Adb.getOutputOfCmd(cmd)
        if len(errStr) > 0:
            return False, Adb.handleErrorMsg(errStr)
        elif len(outStr) > 0:
            return True, outStr
        else:
            return True, 'Not set'
import os
import re
import subprocess

class Adb():
    def __init__(self):
        pass

    @staticmethod
    def uninstallApp(device, pckg):
        try:
            subprocess.check_output(r'adb -s {} uninstall {}'.format(device, pckg))
            return 'Done!'
        except subprocess.CalledProcessError:
            return 'An error occured.'

    @staticmethod
    def isApkDebuggable(build):
        try:
            out = subprocess.check_output(r'aapt dump badging {}'.format(build)).decode().split()
            for i in out:
                if 'application-debuggable' in i:                    
                    return True
            return False
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return 'Aapt not found.'

    @staticmethod
    def deleteFile(device, fullPath):
        try:
            subprocess.check_output(r'adb -s {} shell rm {}'.format(device, fullPath))
            return 'Done deleting'
        except subprocess.CalledProcessError:
            return 'Error!'

    @staticmethod
    def isInstalledPackageDebuggable(device, pckg):
        try:
            out = subprocess.check_output(r'adb -s {} shell dumpsys package {}'.format(device, pckg)).decode().rsplit('\n')
            for i in [j.replace(' ', '') for j in out]:
                if 'flags' in i:
                    if 'DEBUG' in i:
                        return True
            return False
        except subprocess.CalledProcessError:
            return
    
    @staticmethod
    def removeLocalAppData(device, pckg):
        try:
            subprocess.check_output(r'adb -s {} shell pm clear {}'.format(device, pckg))
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def isBuildIsAlreadyInstalled(device, pckg):
        try:
            out = subprocess.check_output(r'adb -s {} shell pm list packages'.format(device)).decode().split()
            for i in out:
                if pckg in i:
                    return True
            return False
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def getPackageNameOfAppFromApk(build):
        try:
            out = subprocess.check_output(r'aapt dump badging {}'.format(build)).decode().split()
            for i in out:
                if 'com.' in i:
                    packageName = i[i.find('com.'):-1]
                    return packageName
        except FileNotFoundError:
            return 'Aapt not found.'
        except subprocess.CalledProcessError:
            return 'An error occured.'

    @staticmethod
    def getBuildVersionFromApk(build):
        try:
            out = subprocess.check_output(r'aapt dump badging {}'.format(build)).decode().split()
            for i in out:
                if 'versionName' in i:
                    return i[i.find('=')+2:-1]
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return 'Aapt not found.'

    @staticmethod
    def getBuildVersionFromDevice(device, pckg):
        try:
            out = subprocess.check_output(r'adb -s {} shell dumpsys package {}'.format(device, pckg)).decode().split()
            for i in out:
                if 'versionName' in i:
                    return i[i.find('=')+1:]
            return False
        except subprocess.CalledProcessError:
            return False

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
                devices.append((i.decode(), tempList[idx+1].decode()))
        return devices
    
    @staticmethod
    def captureScreenshot(device, filename):
        dirOnDevice = os.path.join('sdcard/', filename)
        timeout = 10
        try:
            subprocess.check_output(r'adb -s {} shell screencap "{}"'.format(device, dirOnDevice), timeout = timeout)
            return ('Pulling file...', dirOnDevice)
        except subprocess.CalledProcessError:
            return ('An error occured while taking screenshot!', False)
        except subprocess.TimeoutExpired:
            return ('Timed out! ({}s)'.format(timeout), False)

    @staticmethod
    def pullScreenshot(device, fullPathOnDevice, destinationDirectory):
        timeout = 15
        try:
            subprocess.check_output(r'adb -s {} pull "{}" {}'.format(device, fullPathOnDevice, destinationDirectory))
            return 'Done!'
        except subprocess.CalledProcessError:
            return 'An error ocurred!'
        except subprocess.TimeoutExpired:
            return 'Timed out! ({}s)'.format(timeout)

    @staticmethod
    def installBuild(device, build):
        timeout = 60
        try:
            raw_out = subprocess.check_output(r'adb -s {} install -r "{}"'.format(device, build), timeout = timeout)
            return True
        except subprocess.CalledProcessError:
            return False
        except subprocess.TimeoutExpired:
            return False

    @staticmethod
    def getDeviceIpAddress(device):
        try:
            raw = subprocess.check_output(r"adb -s {} shell ip addr show wlan0".format(device), shell = True).decode().split()
        except subprocess.CalledProcessError:
            return 'couldnt retrieve ip'
        for i in raw:
            if i[0:7] == '192.168':
                return i[0:len(i)-3]
        return 'Not set'

    @staticmethod
    def getDeviceScreenSize(device):
        rawData = subprocess.check_output(r"adb -s {} shell wm size".format(device)).decode().split()
        res = re.sub('x', ' ', rawData[2]).split()
        return "{}x{}".format(res[1], res[0])

    @staticmethod
    def getBatteryStatus(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys battery'.format(device), shell = True).decode().split()
        for idx, i in enumerate(out):
            if i == 'level:':
                return out[idx+1]+'%'

    @staticmethod
    def getPluggedInStatus(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys battery'.format(device), shell = True).decode().split()
        for idx, i in enumerate(out):
            if i == 'AC' or i == 'USB':
                if out[idx+2] == 'true':
                    return 'True, {} powered'.format(i)
        return 'False'

    @staticmethod
    def getOsVersion(device):
        return subprocess.check_output(r'adb -s {} shell getprop ro.build.version.release'.format(device), shell = True)

    @staticmethod
    def getApiVersion(device):
        return subprocess.check_output(r'adb -s {} shell getprop ro.build.version.sdk'.format(device), shell = True)

    @staticmethod
    def getDeviceModel(device):
        return subprocess.check_output(r'adb -s {} shell getprop ro.product.model'.format(device), shell = True).rstrip().decode()

    @staticmethod
    def getDeviceTimezone(device):
        return subprocess.check_output(r'adb -s {} shell getprop persist.sys.timezone'.format(device), shell = True)

    @staticmethod
    def getDeviceLanguage(device):
        lang = subprocess.check_output(r'adb -s {} shell getprop persist.sys.locale'.format(device), shell = True).rstrip()
        if len(lang) > 0:
            return lang
        else:
            return 'N/A'

    @staticmethod
    def getMarketingName(device):
        name = subprocess.check_output(r'adb -s {} shell getprop ro.config.marketing_name'.format(device), shell = True).rstrip()
        if len(name) > 0:
            return name
        else:
            return 'N/A'

    @staticmethod
    def getBrand(device):
        brand = subprocess.check_output(r'adb -s {} shell getprop ro.product.brand'.format(device), shell = True)
        if len(brand) > 0:
            return brand
        else:
            return 'N/A'

    @staticmethod
    def getWifiName(device):
        out = subprocess.check_output(r'adb -s {} shell dumpsys wifi'.format(device), shell = True).decode().split()
        for idx, i in enumerate(out):
            if i == 'mWifiInfo':
                if out[idx+2][1:] == 'unknown':
                    return 'Not set'
                else:
                    return out[idx+2][:-1]

    @staticmethod
    def getListOfHuuugePackages(device):
        packages = []
        list = ('huuuge', 'gamelion')
        output = subprocess.check_output(r'adb -s {} shell pm list packages'.format(device), shell = True).decode().split()
        for i in list:
            for j in output:
                if i in j:
                    packages.append(j)
        return packages[0][8:]
    
    @staticmethod
    def getTcpipPort(device):
        port = subprocess.check_output(r'adb -s {} shell getprop service.adb.tcp.port'.format(device), shell = True).rstrip()
        if len(port) > 0:
            return port
        else:
            return 'Not set'

    @staticmethod
    def getSerialNo(device):
        serial = subprocess.check_output(r'adb -s {} shell getprop ro.boot.serialno'.format(device), shell = True).rstrip()
        if len(serial) > 0:
            return serial
        else:
            return 'Not set'

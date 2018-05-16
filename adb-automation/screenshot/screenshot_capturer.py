import subprocess
import os
from datetime import datetime
import msvcrt
import threading
import json
import re

devicesDataPath = r"\\192.168.64.200\byd-fileserver\MHO\devices.json"
fileDir = r"/sdcard"
destinationDir = os.getcwd()

def takeScreenShot(device):
    subprocess.check_output(r'adb -s {} shell screencap "{}/{}_{}.png"'.format(device, fileDir, getDeviceInfo(device, jsonData), getResolution(device)))
    subprocess.check_output(r'adb -s {} pull "{}/{}_{}.png" {}\output'.format(device, fileDir, getDeviceInfo(device, jsonData), getResolution(device), destinationDir))

def getDevices():
    devices = []
    try:
        _l = subprocess.check_output(r"adb devices")
    except subprocess.CalledProcessError:
        _l = subprocess.check_output(r"adb devices")
    rawList = _l.rsplit()
    tempList = rawList[4:]
    for i in range(len(tempList)):
        if i%2 == 0:
            devices.append(tempList[i].decode())
    print("Devices: {}".format(devices))
    return devices

def createThreads(func, devices):
    threads = []
    for i in devices:
        localThread = threading.Thread(target=func, args=(i,))
        threads.append(localThread)
        localThread.start()
    for j in threads:
        j.join()

def getJsonData(dataPath):
    with open(dataPath, 'r') as f:
        return json.loads(f.read())

def getDeviceInfo(id, data):
    for i in range(len(data['Devices'])):
        if id in data['Devices'][i]['id']:
            return re.sub(' ', '_', data['Devices'][i]['name'])

def getResolution(device):
    rawData = subprocess.check_output(r"adb -s {} shell wm size".format(device)).decode().split()
    res = re.sub('x', ' ', rawData[2]).split()
    return "{}x{}".format(res[1], res[0])

if __name__ == "__main__":
    jsonData = getJsonData(devicesDataPath)
    try:
        createThreads(takeScreenShot, getDevices())
    except:
        createThreads(takeScreenShot, getDevices())
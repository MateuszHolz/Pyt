import subprocess
import os
from datetime import datetime
import msvcrt
import threading

fileDir = r"/sdcard"
fileName = r"_{}.png".format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
destinationDir = os.getcwd()

def takeScreenShot(device):
    subprocess.check_output(r'adb -s {} shell screencap "{}/{}{}"'.format(device, fileDir, device, fileName))
    subprocess.check_output(r'adb -s {} pull "{}/{}{}" {}\output'.format(device, fileDir, device, fileName, destinationDir))

def getDevices():
    devices = []
    rawList = subprocess.check_output(r"adb devices").rsplit()
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

if __name__ == "__main__":
    createThreads(takeScreenShot, getDevices())
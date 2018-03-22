import subprocess
import sys
import installer
import threading

def getCurFileIndx():
    with open('indx.txt', 'r') as f:
        return int(f.read())

def setCurFileIndx():
    with open('indx.txt', 'w') as f:
        f.write(str(indx+1))

indx = getCurFileIndx()
fileDir = r"/sdcard/"
fileName = r"screen_{}.png".format(indx)
destinationDir = r"c:\users\mho\desktop"

adb_shell = subprocess.Popen(r"{}adb shell".format(installer.getPathOfAdb()), stdin = subprocess.PIPE)
print("1")
output = adb_shell.communicate(r"screencap {}\{}".format(fileDir, fileName).encode())
setCurFileIndx()
print("2")
subprocess.Popen(r"{}adb pull {}{} {}".format(installer.getPathOfAdb(), fileDir, fileName, destinationDir))
print("Done")

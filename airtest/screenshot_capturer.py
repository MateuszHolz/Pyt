import subprocess
import sys
import threading
import os

def getCurFileIndx():
    with open('indx.txt', 'r') as f:
        return int(f.read())

def setCurFileIndx():
    with open('indx.txt', 'w') as f:
        f.write(str(indx+1))

indx = getCurFileIndx()
fileDir = r"/sdcard/"
fileName = r"screen_{}.png".format(indx)
destinationDir = os.getcwd()
pathOfAdb = r"c:\users\mho\desktop\pyt\adb-automation\data\platform-tools"

adb_shell = subprocess.Popen(r"{}\adb shell".format(pathOfAdb), stdin = subprocess.PIPE)
print("1")
output = adb_shell.communicate(r"screencap {}\{}".format(fileDir, fileName).encode())
setCurFileIndx()
print("2")
subprocess.Popen(r"{}\adb pull {}{} {}".format(pathOfAdb, fileDir, fileName, destinationDir))
print("Done")

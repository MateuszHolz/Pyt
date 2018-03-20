import subprocess
import sys
import installer
import threading

fileDir = r"/sdcard/"
fileName = r"testowyscreen.jpg"
destinationDir = r"c:\users\mho\desktop"

adb_shell = subprocess.Popen(r"{}adb shell".format(installer.getPathOfAdb()), stdin = subprocess.PIPE)
print("1")
output = adb_shell.communicate("screencap {}\{}".format(fileDir, fileName).encode())
print("2")
subprocess.Popen(r"{}adb pull {}{} {}".format(installer.getPathOfAdb(), fileDir, fileName, destinationDir))

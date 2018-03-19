import subprocess
import sys

adb_shell = subprocess.Popen(r"C:\Users\mho\AppData\Local\Android\sdk\platform-tools\adb shell", stdin = subprocess.PIPE)
print("1")
adb_shell.communicate(b"screencap /sdcard/testscreen.jpg")
print("2")
subprocess.Popen(r"C:\Users\mho\AppData\Local\Android\sdk\platform-tools\adb pull /sdcard/testscreen.jpg c:\users\mho\desktop")

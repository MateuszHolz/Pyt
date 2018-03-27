import json
import msvcrt
import os
import subprocess
import sys
import threading
import time
import re

keyWords = ["huuuge", "gamelion"]

listOfPkg = []

listOfPackages = subprocess.check_output(r"adb shell pm list packages -f")
for i in listOfPackages.decode().split():
    for j in keyWords:
        if j in i:
            print(i)
            localS = i.replace('=', ' ').split()
            listOfPkg.append(localS[len(localS)-1])

print(listOfPkg)
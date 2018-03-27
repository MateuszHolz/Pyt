import json
import msvcrt
import os
import subprocess
import sys
import threading
import time




listOfPackages = subprocess.check_output(r"adb -s ce09171919df3833047e shell pm list packages -f")
for i in listOfPackages.decode().split():
    if "huuuge" in i or "gamelion" in i:
        print(i)


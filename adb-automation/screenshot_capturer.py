import subprocess
import os
from datetime import datetime

fileDir = r"/sdcard"
fileName = r"screen_{}.png".format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
destinationDir = os.getcwd()

subprocess.check_output(r'adb shell screencap "{}/{}"'.format(fileDir, fileName))
subprocess.check_output(r'adb pull "{}/{}" {}'.format(fileDir, fileName, destinationDir))
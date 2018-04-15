import os
from airtest.core.api import *
from airtest.core.device import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import re
import time
import subprocess


connect_device("android:///")
def getLogcat(dir, serialNo):
    with open(dir, 'w', encoding='utf-8') as f:
        f.write(subprocess.check_output(r'c:\users\armin\airtest\airtest\core\android\static\adb\windows\adb.exe -s {} logcat -d'.format(serialNo)).decode('utf-8'))
    return dir
import subprocess

cmd = r'adb -s 9889d64547504e4352 shell dumpsys package com.huuuge.stars.slots'

out = subprocess.check_output(cmd).decode().split()

for i in out:
        if 'versionCode' in i:
                print(i[i.find('=')+1:])
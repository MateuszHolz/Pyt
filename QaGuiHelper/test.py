import subprocess
import os

build = r'C:\Users\mho\Downloads\MagicCasino-debug-slots-gp-dev-5406.apk'

print(os.path.exists(build))

out = subprocess.check_output(r'aapt dump badging "{}"'.format(build)).decode().split()

for i in out:
    if 'com.' in i:
        print(i)
        break
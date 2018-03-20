import subprocess
import re


adb_shell = subprocess.check_output(r"C:\Users\mho\AppData\Local\Android\sdk\platform-tools\adb shell wm size")
print(re.sub(r'x', ' ', adb_shell.decode().rstrip())[15:])
try:
    adb_shell = subprocess.check_output(r"C:\Users\mho\AppData\Local\Android\sdk\platform-tools\adb shell monkey -p com.huuuge.stars.slots 1")
except subprocess.CalledProcessError:
    pass
print(adb_shell)

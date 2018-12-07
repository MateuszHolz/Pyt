import subprocess

cmd = r'adb start-server'

proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
out, err = proc.communicate()
print(out, err)
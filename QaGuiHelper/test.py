import subprocess

cmd = r'adb -s FA87D1F00513 get-state'


process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
output, err = process.communicate()
print(output)

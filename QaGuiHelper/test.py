import subprocess

build = r'C:\Users\mho\Downloads\HuuugeStars-0.1.1497-master-(35a0975d4b759f308c627f1a6ef899b411857aa2)-debug.apk'
device = 'J8AZB76081067GJ'

cmd = r'adb -s {} install -r "{}"'.format(device, build)
process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
out, err = process.communicate()

print('out:', out)
print('err:', err)
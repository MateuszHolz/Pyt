import subprocess

def recurTests():
    subprocess.check_output("python testcase.py")

recurTests()
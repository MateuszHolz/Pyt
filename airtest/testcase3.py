import subprocess

def recurTests():
    try:
        subprocess.check_output("python testcase.py")
    except subprocess.CalledProcessError:
        recurTests()


recurTests()
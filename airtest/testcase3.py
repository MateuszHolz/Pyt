import subprocess
import extended_airtest
import json

def recurTests():
    try:
        subprocess.check_output("python testcase.py")
    except subprocess.CalledProcessError:
        with open('error.json', 'r') as f:
            print("sending mail")
            extended_airtest.sendMail(json.loads(f.read()))

recurTests()
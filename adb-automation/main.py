import os
import subprocess
import sys
import msvcrt
import json

def getPathOfAdb():
    f = open(r"config\path.txt", 'r')
    fx = f.read()
    f.close()
    return fx.rstrip()

def getListOfBuildsToUninstall():
    f = open(r"config\projects.txt", 'r')
    fx = f.read().rsplit()
    f.close()
    return fx

def getPathOfBuilds():
    curDir = os.getcwd()
    buildsDir = r"{}\builds".format(curDir)
    return buildsDir

def getListOfDevicesID():
    listOfID = []
    rawJsonData = open(r"\\192.168.64.200\byd-fileserver\MHO\devices.json", 'r').read()
    jsonData = json.loads(rawJsonData)
    for i in range(len(jsonData['Devices'])):
        listOfID.append(jsonData['Devices'][i]['id'])
    return listOfID

def installBuilds(operation, buildsDir, ext, adbpath, listOfDevices=None):
    print("{} builds...".format(operation))
    builds = os.listdir(buildsDir)
    for i in builds:
        if ext in i:
            if listOfDevices == None:
                print("Trying to install {}...".format(i))
                try:
                    subprocess.check_output(r"{}adb install -r {}\{}".format(adbpath, buildsDir, i))
                    print("Installed package {}".format(i))
                except subprocess.CalledProcessError:
                    continue
        else:
            print("No builds found.")
            break
    print("All operations are done.")

def uninstallExistingBuilds(listOfPkgName, adbpath):
    print("Uninstalling builds...")
    for i in listOfPkgName:
        try:
            print("Uninstalling {} ...".format(i))
            subprocess.check_output(r"{}adb uninstall {}".format(adbpath, i), stderr=subprocess.STDOUT) #"stderr=subprocess.STDOUT" <- silences java exceptions that occur when we try to uninstall non-existent build
        except subprocess.CalledProcessError:
            continue
    print("Uninstalled all existing apps.")

def adbConnectionStatus(adbpath):
    r = subprocess.check_output(r"{}adb devices".format(adbpath))
    return r

def checkAdbConnectionStatus(curStatus):
    status = curStatus != responseToNoDevice
    return status

if __name__ == '__main__':
    extension = ".apk"
    msg1 = ("Uninstall all builds from device (specified in config/builds.txt) and install new apks - type and enter a")
    msg2 = ("Overwrite existing builds with apks - type and enter b")
    listOfIds = getListOfDevicesID()
    print("Checking adb path...")

    try:
        subprocess.check_output(r"{}adb".format(getPathOfAdb()))
    except FileNotFoundError:
        print("Adb hasn't been found. Please enter proper adb path in path.txt file and re-run program.\nPress any key to continue...")
        msvcrt.getch()
        sys.exit()
    except subprocess.CalledProcessError as err:
        if len(err.output) > 5000: #very large output means that everything is fine.
            print("adb found")
            pass
        else:
            print("Something went really wrong.\nPress anything to continue...")
            msvcrt.getch()
            sys.exit()

    print("Checking devices...")
    canProceed = False

    while canProceed == False:
        devicesOutput = adbConnectionStatus(getPathOfAdb())
    for i in devicesOutput.rsplit():
        print(i)

    print("##########################################################\n\nWhat should we do now?\n")

    Input = input("{}\n{}\n".format(msg1, msg2))
    correctInput = False

    while correctInput == False:
        if Input == 'a' or Input == 'A':
            correctInput = True
            uninstallExistingBuilds(getListOfBuildsToUninstall(), getPathOfAdb())
            installBuilds("Installing", getPathOfBuilds(), extension, getPathOfAdb())
        elif Input == 'b' or Input == 'B':
            correctInput = True
            installBuilds("Overwriting", getPathOfBuilds(), extension, getPathOfAdb())
        else:
            Input = input("Didn't recognize your input. Try again.\n")
    print("\nPress any key to close program.")
    msvcrt.getch()
    sys.exit()

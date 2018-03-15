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

def loadJsonData(file):
    jsonData = json.loads(open(file, 'r').read())
    return jsonData

def installBuilds(operation, buildsDir, ext, adbpath, listOfDevices):
    print("{} builds...".format(operation))
    builds = os.listdir(buildsDir)
    for j in listOfDevices:
        for i in builds:
            if ext in i:
                print("Trying to install {} on device {}".format(i, j))
                try:
                    subprocess.check_output(r"{}adb -s {} install -r {}\{}".format(adbpath, j, buildsDir, i))
                    print("Installed package {} on device {}".format(i, j))
                except subprocess.CalledProcessError:
                    continue
            else:
                print("No builds found.")
                break
    print("All operations are done.")

def uninstallExistingBuilds(listOfPkgName, adbpath, listOfDevices):
    print("Uninstalling builds...")
    for j in listOfDevices:
        for i in listOfPkgName:
            try:
                print("Uninstalling {} from device {}".format(i, j))
                print(r"{}adb -s {} uninstall {}".format(adbpath, j, i))
                subprocess.check_output(r"{}adb -s {} uninstall {}".format(adbpath, j, i), stderr=subprocess.STDOUT) #"stderr=subprocess.STDOUT" <- silences java exceptions that occur when we try to uninstall non-existent build
            except subprocess.CalledProcessError:
                continue
    print("Uninstalled all existing apps.")

def adbConnectionStatus(adbpath):
    r = subprocess.check_output(r"{}adb devices".format(adbpath))
    return r

if __name__ == '__main__':
    pathToJson = r"\\192.168.64.200\byd-fileserver\MHO\devices.json"
    extension = ".apk"
    msg1 = ("Uninstall all builds from device (specified in config/builds.txt) and install new apks - type and enter a")
    msg2 = ("Overwrite existing builds with apks - type and enter b")
    devicesJson = loadJsonData(pathToJson)
    idsList = []
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
    rawList = subprocess.check_output(r"{}adb devices".format(getPathOfAdb())).rsplit()
    tempList = rawList[4:] #omitting first 4 elements as they are not neccesary.
    for i in range(len(tempList)):
        if i%2 == 0: #every second element in this list is device's ID
            idsList.append(tempList[i].decode())

    print("##########################################################\n\nWhat should we do now?\n")

    Input = input("{}\n{}\n".format(msg1, msg2))
    correctInput = False

    while correctInput == False:
        if Input == 'a' or Input == 'A':
            correctInput = True
            uninstallExistingBuilds(getListOfBuildsToUninstall(), getPathOfAdb(), idsList)
            installBuilds("Installing", getPathOfBuilds(), extension, getPathOfAdb(), idsList)
        elif Input == 'b' or Input == 'B':
            correctInput = True
            installBuilds("Overwriting", getPathOfBuilds(), extension, getPathOfAdb())
        else:
            Input = input("Didn't recognize your input. Try again.\n")
    print("\nPress any key to close program.")
    msvcrt.getch()
    sys.exit()

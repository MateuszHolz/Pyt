import os
import subprocess
import sys
import msvcrt
import json
import threading

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

def getDeviceInfo(id, data):
    for i in range(len(data['Devices'])):
        if id in data['Devices'][i]['id']:
            return data['Devices'][i]['name']

def overwrite(device):
    installBuilds("Overwriting", getPathOfBuilds(), extension, getPathOfAdb(), device)

def uninstallAndInstall(device):
    uninstallExistingBuilds(getListOfBuildsToUninstall(), getPathOfAdb(), device)
    installBuilds("Installing", getPathOfBuilds(), extension, getPathOfAdb(), device)

def installBuilds(operation, buildsDir, ext, adbpath, device):
    print("{} builds...".format(operation))
    builds = os.listdir(buildsDir)
    for i in builds:
        if ext in i:
            print("Trying to install {} on device {}".format(i, getDeviceInfo(device, devicesJson)))
            try:
                subprocess.check_output(r"{}adb -s {} install -r {}\{}".format(adbpath, device, buildsDir, i))
                print("Installed package {} on device {}".format(i, getDeviceInfo(device, devicesJson)))
            except subprocess.CalledProcessError:
                continue
        else:
            print("No builds found.")
            break
    print("All operations are done.")

def uninstallExistingBuilds(listOfPkgName, adbpath, device):
    print("Uninstalling builds...")
    for i in listOfPkgName:
        try:
            print("Uninstalling {} from device {}".format(i, getDeviceInfo(device, devicesJson)))
            print(r"{}adb -s {} uninstall {}".format(adbpath, device, i))
            subprocess.check_output(r"{}adb -s {} uninstall {}".format(adbpath, device, i), stderr=subprocess.STDOUT) #"stderr=subprocess.STDOUT" <- silences java exceptions that occur when we try to uninstall non-existent build
        except subprocess.CalledProcessError:
            continue
    print("Uninstalled all existing apps.")

if __name__ == '__main__':
    pathToJson = r"\\192.168.64.200\byd-fileserver\MHO\devices.json"
    extension = ".apk"
    msg1 = ("Uninstall all builds from device (specified in config/builds.txt) and install new apks - type and enter a")
    msg2 = ("Overwrite existing builds with apks - type and enter b")
    devicesJson = loadJsonData(pathToJson)
    idsList = []
    canProceed = False
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
    while canProceed == False:
        rawList = subprocess.check_output(r"{}adb devices".format(getPathOfAdb())).rsplit()
        tempList = rawList[4:] #omitting first 4 elements as they are not neccesary.
        if len(tempList) > 0:
            canProceed = True
            for i in range(len(tempList)):
                if i%2 == 0: #every second element in this list is device's ID
                    idsList.append(tempList[i].decode())
            print("Found devices:")
            for i in idsList:
                print(getDeviceInfo(i, devicesJson))
        else:
            print("No devices found. Connect devices to PC and press any key to try again.")
            msvcrt.getch()

    print("##########################################################\n\nWhat should we do now?\n")

    Input = input("{}\n{}\n".format(msg1, msg2))
    correctInput = False

    while correctInput == False:
        if Input == 'a' or Input == 'A':
            correctInput = True
            for i in idsList:
                print(i)
                counter = 1
                threading.Thread(target=uninstallAndInstall, args=(i,)).start()
                print("\n\n\n\n\nSTARTED NEW THREAD \n\n\n\n\n\n")
                counter = counter + 1
        elif Input == 'b' or Input == 'B':
            correctInput = True
            for i in idsList:
                print(i)
                threading.Thread(target=overwrite, args=(i,)).start()
        else:
            Input = input("Didn't recognize your input. Try again.\n")
    print("\nPress any key to close program.")
    msvcrt.getch()
    sys.exit()

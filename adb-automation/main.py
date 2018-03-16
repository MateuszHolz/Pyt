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

def getPathOfBuilds(option):
    localBuildsDir = ""
    if option == "a":
        localBuildsDir = r"{}\builds".format(os.getcwd())
    elif option == "b":
        localBuildsDir = r"C:\users\{}\downloads".format(os.getenv('USERNAME'))
    elif option == "c":
        localBuildsDir = open(r"config\buildsdir.txt", 'r').read().rsplit
    print("Buildsdir: {}".format(localBuildsDir))
    return localBuildsDir

def loadJsonData(file):
    jsonData = json.loads(open(file, 'r').read())
    return jsonData

def getDeviceInfo(id, data):
    for i in range(len(data['Devices'])):
        if id in data['Devices'][i]['id']:
            return data['Devices'][i]['name']

def overwrite(device):
    installBuilds("Overwriting", getPathOfBuilds("a"), extension, adbPath, device)

def uninstallAndInstall(device):
    uninstallExistingBuilds(getListOfBuildsToUninstall(), adbPath, device)
    installBuilds("Installing", getPathOfBuilds("b"), extension, adbPath, device)

def getBuildsToInstall(buildsDir, ext):
    builds = []
    for i in os.listdir(buildsDir):
        if ext in i:
            builds.append("{}\{}".format(buildsDir, i))
    print(builds)
    return builds

def installBuilds(operation, buildsDir, ext, adbpath, device):
    localDevice = getDeviceInfo(device, devicesJson)
    builds = getBuildsToInstall(buildsDir, ext)
    if len(builds)>0:
        for i in builds:
            print("Trying to install {} on device {}".format(i, localDevice))
            try:
                subprocess.check_output(r"{}adb -s {} install -r {}".format(adbpath, device, i))
                print("Installed package {} on device {}".format(i, localDevice))
            except subprocess.CalledProcessError:
                continue
        print("Sucessfully installed all builds on {}".format(localDevice))
    else:
        print("No builds found.")

def uninstallExistingBuilds(listOfPkgName, adbpath, device):
    localDevice = getDeviceInfo(device, devicesJson)
    print("Uninstalling builds from {}".format(localDevice))
    for i in listOfPkgName:
        try:
            subprocess.check_output(r"{}adb -s {} uninstall {}".format(adbpath, device, i), stderr=subprocess.STDOUT) #"stderr=subprocess.STDOUT" <- silences java exceptions that occur when we try to uninstall non-existent build
        except subprocess.CalledProcessError:
            continue
    print("Uninstalled all existing apps from {}".format(localDevice))

if __name__ == '__main__':
    pathToJson = r"\\192.168.64.200\byd-fileserver\MHO\devices.json"
    extension = ".apk"
    msg1 = ("Uninstall all builds from device (specified in config/builds.txt) and install new apks - type and enter a")
    msg2 = ("Overwrite existing builds with apks - type and enter b")
    devicesJson = loadJsonData(pathToJson)
    idsList = []
    canProceed = False
    adbPath = getPathOfAdb()
    threads = []
    print("Checking adb path...")

    try:
        subprocess.check_output(r"{}adb".format(adbPath))
    except FileNotFoundError:
        print("Adb hasn't been found. Please enter proper adb path in path.txt file and re-run program.\nPress any key to continue...")
        msvcrt.getch()
        sys.exit()
    except subprocess.CalledProcessError as err:
        if len(err.output) > 5000: #very large output means that everything is fine.
            print("Adb found.")
            pass
        else:
            print("Something went really wrong.\nPress anything to continue...")
            msvcrt.getch()
            sys.exit()

    print("Checking devices...")
    while canProceed == False:
        rawList = subprocess.check_output(r"{}adb devices".format(adbPath)).rsplit()
        tempList = rawList[4:] #omitting first 4 elements as they are not neccesary.
        if len(tempList) > 0:
            canProceed = True
            for i in range(len(tempList)):
                if i%2 == 0: #every second element in this list is device's ID
                    idsList.append(tempList[i].decode())
            print("Found devices:")
            if len(idsList) > 0:
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
                localThread = threading.Thread(target=uninstallAndInstall, args=(i,), name=i)
                threads.append(localThread)
                localThread.start()
        elif Input == 'b' or Input == 'B':
            correctInput = True
            for i in idsList:
                localThread = threading.Thread(target=overwrite, args=(i,))
                threads.append(localThread)
                localThread.start()
        else:
            Input = input("Didn't recognize your input. Try again.\n")
    for i in threads:
        i.join()
    Print("All jobs done. Press any key to exit program.")
    msvcrt.getch()
    sys.exit()

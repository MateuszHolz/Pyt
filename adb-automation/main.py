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
        try:
            localBuildsDir = open(r"config\buildsdir.txt", 'r').read().rsplit
        except FileNotFoundError:
            print("File buildsdir.txt not found. Press any key to terminate program and try again.")
            msvcrt.getch()
            sys.exit()
    return localBuildsDir

def loadJsonData(file):
    jsonData = json.loads(open(file, 'r').read())
    return jsonData

def getDeviceInfo(id, data):
    for i in range(len(data['Devices'])):
        if id in data['Devices'][i]['id']:
            return data['Devices'][i]['name']

def overwrite(device, optionChosen):
    installBuilds("Overwriting", getPathOfBuilds(optionChosen), extension, getPathOfAdb(), device)

def uninstallAndInstall(device, optionChosen):
    uninstallExistingBuilds(getListOfBuildsToUninstall(), getPathOfAdb(), device)
    installBuilds("Installing", getPathOfBuilds(optionChosen), extension, getPathOfAdb(), device)

def getBuildsToInstall(buildsDir, ext):
    builds = []
    for i in os.listdir(buildsDir):
        if ext in i:
            builds.append("{}\{}".format(buildsDir, i))
    return builds

def getUserBuildsOption():
    correctInput = False
    while correctInput == False:
        input1 = input("{}\n{}\n{}\n".format(buildInfo1, buildInfo2, buildInfo3))
        if input1 == 'a' or input1 == 'b' or input1 == 'c':
            correctInput = True
            return input1
        else:
            print("Incorrect input, please try again.")

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

def checkAdbConnection(adbPath):
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

def getDevicesList(idsList, adbPath):
    canProceed = False
    while canProceed == False:
        rawList = subprocess.check_output(r"{}adb devices".format(adbPath)).rsplit()
        tempList = rawList[4:] #omitting first 4 elements as they are static & not neccesary.
        if len(tempList) > 0:
            canProceed = True
            for i in range(len(tempList)):
                if i%2 == 0: #every second element in this list is device's ID
                    idsList.append(tempList[i].decode())
            print("Found devices:")
            if len(idsList) > 0:
                for i in idsList:
                    print(getDeviceInfo(i, devicesJson))
            return idsList
        else:
            print("No devices found. Connect devices to PC and press any key to try again.")
            msvcrt.getch()
def askForInputAboutOptionToInstall():
    Input = input("{}\n{}\n".format(msg1, msg2))
    return Input

def finalInstallationFlow(idList, userInput):
    correctInput = False
    threads = []
    while correctInput == False:
        if userInput == 'a' or userInput == 'A':
            correctInput = True
            for i in idList:
                localThread = threading.Thread(target=uninstallAndInstall, args=(i, userInput))
                threads.append(localThread)
                localThread.start()
        elif userInput == 'b' or userInput == 'B':
            correctInput = True
            for i in idList:
                localThread = threading.Thread(target=overwrite, args=(i, userInput))
                threads.append(localThread)
                localThread.start()
        else:
            userInput = askForInputAboutOptionToInstall()
    for i in threads:
        i.join()

if __name__ == '__main__':
    pathToJson = r"\\192.168.64.200\byd-fileserver\MHO\devices.json"
    extension = ".apk"
    msg1 = "Uninstall all builds from device (specified in config/builds.txt) and install new apks - type and enter a"
    msg2 = "Overwrite existing builds with apks - type and enter b"
    buildInfo1 = r"To get builds from default folder builds in applications directory - type and enter a"
    buildInfo2 = r"To get builds from downloads folder from your PC - type and enter b (downloads directory = c:\users\current_user\downloads)"
    buildInfo3 = r"To get builds from specified path in buildsdir.txt file in config folder - type and enter c"
    devicesJson = loadJsonData(pathToJson)
    ### Checking adb path ###
    print("Checking adb path...")
    checkAdbConnection(getPathOfAdb())

    ### Checking status of connected devices ###
    print("Checking devices...")
    idsList = getDevicesList(idsList, getPathOfAdb())

    ### Asking user for his input regarding installing builds from different directories ###
    userBuildsOptionChosen = getUserBuildsOption()

    print("##########################################################\n\nWhat should we do now?\n")

    finalInstallationFlow(idsList, askForInputAboutOptionToInstall())
    print("All jobs done. Press any key to exit program.")
    msvcrt.getch()
    sys.exit()

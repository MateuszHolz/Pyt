import os
import subprocess
import sys
import msvcrt
import json
import threading
import time

class unauthorizedIndex():
    def __init__(self):
        self.index = 0
    def addUnauthIndex(self):
        self.index += 1
    def getUnauthIndex(self):
        return self.index

def getPathOfAdb():
    return r"data\platform-tools"

def getListOfBuildsToUninstall():
    f = open(r"data\config\projects.txt", 'r')
    fx = f.read().rsplit()
    f.close()
    return fx

def getPathOfBuilds(option):
    localBuildsDir = ""
    if option == "a" or option == "A":
        localBuildsDir = r"{}\data\builds".format(os.getcwd())
    elif option == "b" or option == "B":
        localBuildsDir = r"C:\users\{}\downloads".format(os.getenv('USERNAME'))
    elif option == "c" or option == "C":
        try:
            localBuildsDir = open(r"data\config\buildsdir.txt", 'r').read().rsplit()[0]
        except IndexError:
            print("Error occured. File buildsdir.txt can't be empty.")
            sys.exit()
        except FileNotFoundError:
            print("File buildsdir.txt not found. Make sure file exists. Press any key to terminate program and try again.")
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
    try:
        for i in os.listdir(buildsDir):
            if ext in i:
                builds.append(r"{}\{}".format(buildsDir, i))
    except FileNotFoundError:
        print("Path '{}' not found. Please provide correct path in buildsdir.txt".format(buildsDir))
        sys.exit()
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
                subprocess.check_output(r'{}\adb -s {} install -r "{}"'.format(adbpath, device, i), timeout=60)
                print("Installed package {} on device {}".format(i, localDevice))
            except subprocess.CalledProcessError:
                continue
            except subprocess.TimeoutExpired:
                print("Device {} timed out (60s).".format(localDevice))
                sys.exit()
        print("Finished all jobs on {}".format(localDevice))
    else:
        print("No builds found.")

def uninstallExistingBuilds(listOfPkgName, adbpath, device):
    localDevice = getDeviceInfo(device, devicesJson)
    print("Uninstalling builds from {}".format(localDevice))
    for i in listOfPkgName:
        try:
            print("Uninstalling {} on {}".format(i, localDevice))
            subprocess.check_output(r"{}\adb -s {} uninstall {}".format(adbpath, device, i), stderr=subprocess.STDOUT, timeout=15) #"stderr=subprocess.STDOUT" <- silences java exceptions that occur when we try to uninstall non-existent build
        except subprocess.CalledProcessError:
            continue
        except subprocess.TimeoutExpired:
            print("Device {} timed out.".format(localDevice))
            sys.exit()
    print("Uninstalled all existing apps from {}".format(localDevice))

def checkAdbConnection(adbPath):
    try:
        subprocess.check_output(r"{}\adb".format(adbPath))
    except FileNotFoundError:
        print("Adb hasn't been found. Please re-run program. If problem persists - contact MHO")
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

def getDevicesList(adbPath):
    idsList = []
    canProceed = False
    while canProceed == False:
        rawList = subprocess.check_output(r"{}\adb devices".format(adbPath)).rsplit()
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

def finalInstallationFlow(idList, inputBuildsDirOption):
    correctInput = False
    threads = []
    while correctInput == False:
        inputInstallOption = askForInputAboutOptionToInstall()
        if inputInstallOption == 'a' or inputInstallOption == 'A':
            correctInput = True
            for i in idList:
                localThread = threading.Thread(target=uninstallAndInstall, args=(i, inputBuildsDirOption))
                threads.append(localThread)
                localThread.start()
                time.sleep(1)
        elif inputInstallOption == 'b' or inputInstallOption == 'B':
            correctInput = True
            for i in idList:
                localThread = threading.Thread(target=overwrite, args=(i, inputBuildsDirOption))
                threads.append(localThread)
                localThread.start()
        else:
            print("Incorrect input, please try again.")

    for i in threads:
        i.join()

def checkAuthorization(deviceID, adbpath, keyWord, index):
    print("Checking authorization of {}".format(getDeviceInfo(deviceID, devicesJson)))
    try:
        subprocess.check_output(r'{}\adb -s {} get-state'.format(adbpath, deviceID), stderr=subprocess.STDOUT)
        print("Device {} authorized.".format(getDeviceInfo(deviceID, devicesJson)))
    except subprocess.CalledProcessError as err:
        if keyWord.encode() in err.output:
            print("Device {} unauthorized. Program will now exit. Press any key.".format(getDeviceInfo(deviceID, devicesJson)))
            index.addUnauthIndex()
            msvcrt.getch()
        else:
            print("Device {} authorized.".format(getDeviceInfo(deviceID, devicesJson)))

def createAuthThreads(deviceList, index):
    localThreads = []
    for i in deviceList:
        localThread = threading.Thread(target=checkAuthorization, args=(i, getPathOfAdb(), unauthorizedKeyWord, index))
        localThreads.append(localThread)
        localThread.start()
    for i in localThreads:
        i.join()

if __name__ == '__main__':
    pathToJson = r"\\192.168.64.200\byd-fileserver\MHO\devices.json"
    extension = ".apk"
    msg1 = "Uninstall all builds from device (specified in config/builds.txt) and install new apks - type and enter a"
    msg2 = "Overwrite existing builds with apks - type and enter b"
    buildInfo1 = r"To get builds from default folder builds in applications directory - type and enter a"
    buildInfo2 = r"To get builds from downloads folder from your PC - type and enter b (downloads directory = c:\users\current_user\downloads)"
    buildInfo3 = r"To get builds from specified path in buildsdir.txt file in config folder - type and enter c"
    unauthorizedKeyWord = "unauthorized"
    devicesJson = loadJsonData(pathToJson)
    ### Checking adb path ###
    print("Checking adb path...")
    checkAdbConnection(getPathOfAdb())

    ### Checking status of connected devices ###
    print("Checking devices...")
    idsList = getDevicesList(getPathOfAdb())

    ### Checking authorization of all devices ###
    index = unauthorizedIndex()
    createAuthThreads(idsList, index)
    if index.getUnauthIndex() > 0:
        sys.exit()

    ### Asking user for his input regarding installing builds from different directories ###
    userBuildsOptionChosen = getUserBuildsOption()

    ### Asking user to chose option
    finalInstallationFlow(idsList, userBuildsOptionChosen)

    ### ~ Waiting for all threads to finish ~ ###
    print("Press any key to exit program.")
    msvcrt.getch()
    sys.exit()

import json
import msvcrt
import os
import subprocess
import sys
import threading
import time

extension = ".apk"
msg1 = "Uninstall all builds from device (specified in config/builds.txt) and install new apks - type and enter a"
msg2 = "Overwrite existing builds with apks - type and enter b"
buildInfo1 = r"To get builds from default folder builds in applications directory - type and enter a"
buildInfo2 = r"To get builds from downloads folder from your PC - type and enter b (downloads directory = c:\users\current_user\downloads)"
buildInfo3 = r"To get builds from specified path in buildsdir.txt file in config folder - type and enter c"
unauthorizedKeyWord = "unauthorized"
devicesDataDir = r"data\config\devicesdir.txt"
projectsDataDir = r"data\config\projects.txt"


class unauthorizedIndex():

    def __init__(self):
        self.index = 0

    def addUnauthIndex(self):
        self.index += 1

    def getUnauthIndex(self):
        return self.index


def getPathOfAdb():
    return r"data\platform-tools"


def getListOfBuildsToUninstall(projectsDir):
    try:
        return open(projectsDir, 'r').read().rsplit()
    except FileNotFoundError:
        print("{} not found. Press any key...".format(projectsDir))
        msvcrt.getch()
        sys.exit()


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
    jsonData = {}
    try:
        jsonData = json.loads(open(file, 'r').read())
        return jsonData
    except FileNotFoundError:
        print("Couldn't find {} directory.\nIf you're not from BYD consider creating one yourself (pm @mho on slack for more info),\nplace it in fileserver directory and copy its path to data/config/devicesdir.txt file.\nIf you are from BDG and see this msg - contact @mho.".format(getDevicesDir(devicesDataDir)))
        return jsonData


def getDeviceInfo(id, data):
    try:
        for i in range(len(data['Devices'])):
            if id in data['Devices'][i]['id']:
                return data['Devices'][i]['name']
        return id
    except KeyError:
        return id


def overwrite(device, optionChosen, builds = None):
    installBuilds("Overwriting", getPathOfBuilds(optionChosen), extension, getPathOfAdb(), device, builds)


def uninstallAndInstall(device, optionChosen, builds = None):
    uninstallExistingBuilds(getListOfBuildsToUninstall(projectsDataDir), getPathOfAdb(), device)
    installBuilds("Installing", getPathOfBuilds(optionChosen), extension, getPathOfAdb(), device, builds)


def getBuildsToInstall(buildsDir, ext):
    builds = []
    try:
        for i in os.listdir(buildsDir):
            if ext in i:
                builds.append(r"{}\{}".format(buildsDir, i))
    except FileNotFoundError:
        print("Path '{}' not found.".format(buildsDir))
        sys.exit()
    return builds


def getUserBuildsOption():
    correctInput = False
    while correctInput == False:
        try:
            input1 = input("{}\n{}\n{}\n".format(buildInfo1, buildInfo2, buildInfo3))
            if input1 == 'a' or input1 == 'b' or input1 == 'c':
                correctInput = True
                return input1
            else:
                print("Incorrect input, please try again.")
        except EOFError:
            print("Incorrect input, please try again.")
            pass


def installBuilds(operation, buildsDir, ext, adbpath, device, builds = None):
    localDevice = getDeviceInfo(device, devicesJson)
    if builds == None:
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
        print("No builds found in directory: {}".format(buildsDir))


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
            print("Device {} timed out. Trying to uninstall {} once again".format(localDevice, i))
            try:
                subprocess.check_output(r"{}\adb -s {} uninstall {}".format(adbpath, device, i), stderr=subprocess.STDOUT, timeout=15)
            except subprocess.TimeoutExpired:
                print("Device {} timed out once again. Omitting {}.".format(localDevice, i))
                pass
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


def getDevicesList(adbPath, devJson):
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
                    if len(devJson) > 0:
                        print(getDeviceInfo(i, devJson))
                    else:
                        print(i)
            return idsList
        else:
            print("No devices found. Connect devices to PC and press any key to try again.")
            msvcrt.getch()


def askForInputAboutOptionToInstall():
    correctInput = False
    while correctInput == False:
        try:
            Input = input("{}\n{}\n".format(msg1, msg2))
            correctInput = True
        except EOFError:
            print("Incorrect input, please try again.")
    return Input


def finalInstallationFlow(idList, inputBuildsDirOption, builds = None):
    correctInput = False
    threads = []
    while correctInput == False:
        inputInstallOption = askForInputAboutOptionToInstall()
        if inputInstallOption == 'a' or inputInstallOption == 'A':
            correctInput = True
            for i in idList:
                localThread = threading.Thread(target=uninstallAndInstall, args=(i, inputBuildsDirOption, builds))
                threads.append(localThread)
                localThread.start()
                time.sleep(1)
        elif inputInstallOption == 'b' or inputInstallOption == 'B':
            correctInput = True
            for i in idList:
                localThread = threading.Thread(target=overwrite, args=(i, inputBuildsDirOption, builds))
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


def getDevicesDir(devicesDir):
    try:
        data = open(devicesDir, 'r').read().rstrip()
        if len(data) > 0:
            return data
        else:
            userInput = input("File {} is empty! Enter y to proceed, enter any other character to terminate program. ".format(devicesDir))
            if userInput == 'Y' or userInput == 'y':
                return 'Empty_Dir'
            else:
                sys.exit()
    except FileNotFoundError:
        print("{} not found. Press any key to close program.".format(devicesDir))
        msvcrt.getch()
        sys.exit()


if __name__ == '__main__':
    _builds = None
    userBuildsOptionChosen = None
    os.chdir(os.path.dirname(sys.argv[0]))

    ### Checking adb path ###
    print("Checking adb path...")
    checkAdbConnection(getPathOfAdb())
    ### Checking status of connected devices ###
    devicesJson = loadJsonData(getDevicesDir(devicesDataDir))
    print("Checking devices...")
    idsList = getDevicesList(getPathOfAdb(), devicesJson)

    ### Checking authorization of all devices ###
    index = unauthorizedIndex()
    createAuthThreads(idsList, index)
    if index.getUnauthIndex() > 0: # true means that at least one device is unauthorized
        sys.exit()

    ### Checking if user has dropped builds to install. If so, prompting all builds that were dropped, checking if all end with .apk ###
    if len(sys.argv) > 1:
        for i in sys.argv[1:]:
            if not ".apk" in i:
                print("{} <----- is not a build. Please drag only builds. Press any key to exit...".format(i))
                msvcrt.getch()
                exit()
        _builds = sys.argv[1:]
        print("Following builds will be installed:")
        for i in _builds:
            print(i)
    else:
        ### Asking user for his input regarding installing builds from different directories ###
        userBuildsOptionChosen = getUserBuildsOption()

    finalInstallationFlow(idsList, userBuildsOptionChosen, _builds)

    ### ~ Waiting for all threads to finish ~ ###
    print("Press any key to exit program.")
    msvcrt.getch()
    sys.exit()

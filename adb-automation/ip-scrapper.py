import json
import msvcrt
import subprocess
import sys
import threading


devicesDataPath = r"\\192.168.64.200\byd-fileserver\MHO\devices.json"
pathOfAdb = r"data\platform-tools"
unauthorizedKeyWord = "unauthorized"
outputFile = r"ip_adresses.txt"


class unauthorizedIndex():
    def __init__(self):
        self.index = 0

    def addUnauthIndex(self):
        self.index += 1

    def getUnauthIndex(self):
        return self.index


def getJsonData(dataPath):
    jsonData = json.loads(open(dataPath, 'r').read())
    return jsonData


def getDeviceInfo(id, data):
    for i in range(len(data['Devices'])):
        if id in data['Devices'][i]['id']:
            return data['Devices'][i]['name']


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


def checkAuthorization(deviceID, adbpath, keyWord, index, devicesJson):
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


def createAuthThreads(deviceList, index, adbpath, authFunction, devicesJson):
    localThreads = []
    for i in deviceList:
        localThread = threading.Thread(target=authFunction, args=(i, adbpath, unauthorizedKeyWord, index, devicesJson))
        localThreads.append(localThread)
        localThread.start()
    for i in localThreads:
        i.join()


def getDevicesList(adbPath, devicesJson):
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


def writeIpAdresses(deviceIdList, deviceDataDict, adbpath, outputFile):
    with open(outputFile, 'w') as file:
        for i in deviceIdList:
            ipAdress = subprocess.check_output(r"{}\adb -s {} shell ip addr show wlan0".format(adbpath, i)).decode().split()
            for j in ipAdress:
                if j[0:7] == '192.168':
                    file.write("{} - {}\n".format(getDeviceInfo(i, deviceDataDict), j[0:len(j)-3]))
                    break


if __name__ == "__main__":
    ### Initializing needed resources ###
    devicesData = getJsonData(devicesDataPath)
    index = unauthorizedIndex()
    devicesList = getDevicesList(pathOfAdb, devicesData)

    ### Checking adb path ###
    checkAdbConnection(pathOfAdb)

    ### Checking authorization of devices ###
    createAuthThreads(devicesList, index, pathOfAdb, checkAuthorization, devicesData)
    if index.getUnauthIndex() > 0:
        sys.exit()

    ### Retrieving ip addresses and saving them to file ###
    writeIpAdresses(devicesList, devicesData, pathOfAdb, outputFile)
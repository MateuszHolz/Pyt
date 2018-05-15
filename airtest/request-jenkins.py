import requests
import os
import testcase as testcase
import time
from datetime import datetime

link = 'http://byd.jenkins.game-lion.com:8080/view/Huuuge%20Stars/view/Client%20Dev/job/huuuge-stars/job/client-dev/job/hs-android/lastSuccessfulBuild/artifact/output/'
login = 'qa'
passwrd = 'HuuugeQA!2016'

class buildNameContainer():

    def __init__(self):
        self.name = None

    def setName(self, newName):
        self.name = newName

    def getName(self):
        return self.name

def printW(str):
    print('[{}] {}'.format(datetime.now().strftime('%X'), str))

def getBuildNameFromSite():
    req = requests.get(link, auth=(login, passwrd))
    for i in req.text.split():
        if "HuuugeStars" in i:
            id1 = i.find("HuuugeStars")
            id2 = i.find(".apk")+4
            return i.rstrip()[id1:id2]
            break

def isNewBuild(buildNameCont):
    build = getBuildNameFromSite()
    if build == buildNameCont.getName():
        printW('{} already checked before.'.format(build))
        return False
    else:
        printW('{} hasnt been checked yet.'.format(build))
        buildNameCont.setName(build)
        downloadBuild(build)
        return '{}\\{}'.format(os.getcwd(), build)

def downloadBuild(path):
    printW('Downloading {} ...'.format(path))
    r = requests.get("{}{}".format(link, path), auth=('qa','HuuugeQA!2016'), stream=True)
    with open(path, 'wb') as file:
        file.write(r.content)
    return

if __name__ == '__main__':
    # Initialize name container #
    nameContainer = buildNameContainer()
    while True:
        if isNewBuild(nameContainer):
            printW('New build has been found - {}. Starting tests.'.format(nameContainer.getName()))
            testcase.deployTest(nameContainer.getName())
        else:
            printW('Didnt find any new build. Waiting 20 minutes...')
            time.sleep(1200)

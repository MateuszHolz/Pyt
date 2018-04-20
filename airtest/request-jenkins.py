import requests
import os
import testcase as testcase
import time

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
        print('{} already checked before.'.format(build))
        return False
    else:
        print('{} hasnt been checked yet.'.format(build))
        buildNameCont.setName(build)
        downloadBuild(build)
        return '{}\\{}'.format(os.getcwd(), build)

def downloadBuild(path):
    print('Downloading {} ...'.format(path))
    r = requests.get("http://byd.jenkins.game-lion.com:8080/view/Huuuge%20Stars/view/Client%20Dev/job/huuuge-stars/job/client-dev/job/hs-android/lastSuccessfulBuild/artifact/output/{}".format(path), auth=('qa','HuuugeQA!2016'), stream=True)
    with open(path, 'wb') as file:
        file.write(r.content)
    return

if __name__ == '__main__':
    # Initialize name container #
    nameContainer = buildNameContainer()
    while True:
        if isNewBuild(nameContainer):
            print('New build has been found - {}. Starting tests.'.format(nameContainer.getName()))
            testcase.deployTest(nameContainer.getName())
        else:
            print('Didnt find any new build. Waiting 10 minutes...')
            time.sleep(600)

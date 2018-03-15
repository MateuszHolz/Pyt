import json
import re

def loadFile(path):
    localFile = open(path, 'r')
    fileContent = localFile.read()
    return fileContent

def getList(jsonData, typeOfList):
    localList = []
    for i in range(len(jsonData['Records'])):
        if typeOfList == 0 or typeOfList == 1:
            localList.append(jsonData['Records'][i]['s3']['bucket']['name'])
            if typeOfList == 0: # PROJECT NAMES
                localList[i] = re.sub("-", " ", localList[i]).split()[2]
            elif typeOfList == 1: # BUCKET NAMES
                continue
        elif typeOfList == 2: # DATE OF EVENT
            localList.append(jsonData['Records'][i]['s3']['object']['key'][5:15])
        else:
            return None
    return localList

if __name__ == "__main__":
    pathOfFile = "events.json"
    content = json.loads(loadFile(pathOfFile))
    for i, j, k in zip(getList(content, 0), getList(content, 1), getList(content, 2)):
        print("Project: {}, Bucket Name: {}, Date of Event: {}".format(i, j, k))

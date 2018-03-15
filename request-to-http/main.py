import http.client
import json
import copy
import msvcrt

def getBearerId():
    localFile = open("bearer.txt", 'r')
    id = localFile.read()
    localFile.close()
    return id.rstrip()

def getBody():
    localFile = open("body.json", 'r')
    body = localFile.read()
    localFile.close()
    return body

def runQuerry(connection, amountOfQuerries, shouldAddIndex, listIDS):
    globalBody = json.loads(getBody())
    localBody = copy.deepcopy(globalBody)
    createdEntries = 0
    for i in range(int(amountOfQuerries)):
        if shouldAddIndex:
            localBody['name'] = globalBody['name'] + str(i)
            connection.request("POST", '/ht/config/queries', body=json.dumps(localBody), headers=header)
            response = connection.getresponse()
            localResponse = response.read()
            createdEntries = createdEntries + 1
            print("Status code: {}, message: {}".format(response.status, response.reason))
        else:
            connection.request("POST", '/ht/config/queries', body=json.dumps(globalBody), headers=header)
            response = conn.getresponse()
            response.read()
            localResponse = response.read()
            createdEntries = createdEntries + 1
            print("Status code: {}, message: {}".format(response.status, response.reason))
    print("Successfully created {} entires.".format(createdEntries))
def getConfig(idx): # 0=liczbaQuerry, 1=numerowanieID
    localFile = open("config.json", 'r')
    jsonData = json.loads(localFile.read())
    localFile.close()
    if(idx == 0):
        return jsonData['liczbaQuerry']
    elif(idx == 1):
        return jsonData['numerowanieID']
    else:
        raise TypeError("ID out of possible range")

header = {"Content-type": "application/json", "Authorization": "Bearer {}".format(getBearerId())}
conn = http.client.HTTPSConnection('ai6u732cj7.execute-api.us-east-1.amazonaws.com')
listaID = []

runQuerry(conn, getConfig(0), getConfig(1), listaID)
print("\nPress any key to continue")
msvcrt.getch()
conn.close()

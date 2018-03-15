import http.client
import json
import copy

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
            print(json.loads(localResponse))
            listIDS.append(json.loads(localResponse)['id'])
            createdEntries = createdEntries + 1
            print("Status code: {}, message: {}, entry ID: {}".format(response.status, response.reason, json.loads(localResponse)['id']))
        else:
            connection.request("POST", '/ht/config/queries', body=json.dumps(globalBody), headers=header)
            response = conn.getresponse()
            response.read()
            localResponse = response.read()
            listIDS.append(json.loads(localResponse)['id'])
            createdEntries = createdEntries + 1
            print("Status code: {}, message: {}, entry ID: {}".format(response.status, response.reason, json.loads(localResponse)['id']))
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

def clearCreatedEntries(connection, listOfID):
    for i in listOfID:
        connection.request("DELETE", '/ht/adhoc/{}'.format(i))
        response = connection.getresponse()
        response.read()
        print(response.status, response.reason)
        print("Cleared entry id: {}".format(i))

header = {"Content-type": "application/json", "Authorization": "Bearer {}".format(getBearerId())}
conn = http.client.HTTPSConnection('ai6u732cj7.execute-api.us-east-1.amazonaws.com')
listaID = []

runQuerry(conn, getConfig(0), getConfig(1), listaID)
localChar = input("Clear just created entries? y/n ")
if(localChar == 'y'):
    clearCreatedEntries(conn, listaID)
else:
    print("No entries have been deleted.")
conn.close()

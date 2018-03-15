import json

dir = r'\\192.168.64.200\byd-fileserver\MHO\data.json'

file = open(dir, 'r')
content = file.read()
content = content.rstrip()
content = json.loads(content)
for i in range(len(content['Devices'])):
    print(content['Devices'][i]['id'])

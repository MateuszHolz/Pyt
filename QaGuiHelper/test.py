import json

data = {}
with open('links.json', 'r') as f:
    data = json.loads(f.read())

for i in data.keys():
    for j in data[i].keys():
        for k in data[i][j].keys():
            print(i, j, k)

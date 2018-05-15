import operator


with open('c:\\users\\armin\\desktop\\lic2.txt', 'r') as f:
    data = f.read().split()

print(len(data))

wordsCounter = {}

for i in range(len(data)):
    if ',' in data[i]:
        data[i] = data[i][:len(data[i])-1] #removing all unneccesary commas

for i in data:
    i = i.lower()
    if i in wordsCounter:
        wordsCounter[i] += 1
        pass
    else:
        wordsCounter[i] = 1

sortedWordsCounter = sorted(wordsCounter.items(), key=operator.itemgetter(1))
print(sortedWordsCounter)
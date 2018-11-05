import requests

url = 'http://byd.jenkins.game-lion.com:8080/view/Huuuge%20Stars/view/Client%20Dev/job/huuuge-stars/job/client-dev/job/hs-ios/lastSuccessfulBuild/'
user = 'mho'
pw = 'wtdrgad7JHr5yzeJ'


response = requests.get(url, auth = (user, pw))

print(response.text.split())
for i in response.text.split():
    if('HuuugeStars') in i:
        print(i)
# import requests

# url = 'http://byd.jenkins.game-lion.com:8080/view/Huuuge%20Stars/view/Client%20Dev/job/huuuge-stars/job/client-dev/job/hs-android/lastSuccessfulBuild/'
# user = 'mho'
# pw = 'wtdrgad7JHr5yzeJ'


# response = requests.get(url, auth = (user, pw))

# print(response.text[response.text.find('HuuugeStars-0.1.1358-master-(50d67955395b900323f26bb612b53db45262808e)-debug.apk'):response.text.find('HuuugeStars-0.1.1358-master-(50d67955395b900323f26bb612b53db45262808e)-debug.apk')+300])



# # with open('build.apk', 'wb') as f:
# #     total_lenght = 88.43*1048576
# #     progress = 0
# #     for b in response.iter_content(chunk_size = 4096):
# #         progress += len(b)
# #         f.write(b)
# #         print(str((progress / total_lenght) * 100)[:4]+'%')
import os
path1 = 'desktop\dupa'
path2 = 'build.apk'
print(os.path.join(path1, path2))
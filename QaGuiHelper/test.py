import requests
import sys

cmd = r'adb start-server'
url = "https://www3999.playercdn.net/185/0/YU2prL5PaX0xjiNiL1D3og/1546642788/180728/dYQIGYFu4GQjHU4.mp4"

file_name = 'chirurdzy-s02-e13'

with open(file_name, 'wb') as file:
    h = requests.head(url)
    # fileSize = h.headers['Content-Lenght']
    print(type(h.headers))
    # print(fileSize)
    r = requests.get(url, stream = True)
    chunkSize = 1024
    downloadedData = 0
    for data in r.iter_content(chunk_size = chunkSize):
        downloadedData += len(data)
        print('Downloaded: {}mb, {}%'.format(downloadedData/10**7, (downloadedData/fileSize)*100))
        file.write(data)




#with open(file_name, 'wb') as f:



# print("Downloading: %s Bytes: %s" % (file_name, file_size))

# file_size_dl = 0
# block_sz = 8192
# while True:
#     buffer = u.read(block_sz)
#     if not buffer:
#         break

#     file_size_dl += len(buffer)
#     f.write(buffer)
#     status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
#     status = status + chr(8)*(len(status)+1)
#     print()

# f.close()
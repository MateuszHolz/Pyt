import requests
import os
import time
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import re
import subprocess

path = 'C:\\users\\mho\\desktop\\scores.txt'
urlToMatches = 'http://www.realmadryt.pl/index.php?co=mecze&kadra=1'
auth = ('testergamelion66@gmail.com', 'dupa1212')

def sendMail(auth, takeImage = None, serialNo = None, bodyTxt = None, subject = None):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(auth[0], auth[1])
    msg = MIMEMultipart()
    if subject:
        msg['Subject'] = subject
    server.sendmail(auth[0], "holz.mateusz@gmail.com", msg.as_string())

def getContentOfWebpage():
    return requests.get(urlToMatches).text.splitlines()

def getListOfMatches(req):
    listaMeczy = []
    for i in req:
        if 'Real -' in i:
            s1 = i.index('id_pilkarz=">')+13
            s2 = i.index('</a></td></tr>')
            listaMeczy.append(i[s1:s2])
        elif '- Real' in i:
            s1 = i.index('id_pilkarz=">')+13
            s2 = i.index('</a></td></tr>')
            listaMeczy.append(i[s1:s2])
    return listaMeczy

def verifyFile(mlist):
    if(os.path.isfile(path)):
        pass
    else:
        with open(path, 'w', encoding='utf-8') as f:
            for i in mlist:
                f.write(i+'\n')

def getContentOfFile(f):
    with open(f, 'r', encoding='utf-8') as f:
        c = f.readlines()
    for i in range(len(c)):
        c[i] = c[i].rstrip()
    return c

def saveNewList(l, f):
    with open(f, 'w', encoding='utf-8') as f:
        for i in l:
            f.write(i+'\n')
    
if __name__ == '__main__':
    _list = getListOfMatches(getContentOfWebpage())
    verifyFile(_list)

    curList = getContentOfFile(path)
    while True:
        newList = getListOfMatches(getContentOfWebpage())

        if curList[0] == newList[0]:
            print('{} = {}'.format(curList[0], newList[0]))
            time.sleep(15)
        else:
            curList.insert(0, newList[0])
            sendMail(auth, subject = curList[0])
            saveNewList(curList, path)
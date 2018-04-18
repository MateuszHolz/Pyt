import extended_airtest as test
from airtest.core.api import *
from airtest.core.device import *
from email.mime.text import MIMEText
import smtplib
from datetime import datetime

if __name__ == "__main__":
    time1 = datetime.now()
    connect_device("android:///")
    for i in range(200):
        test_section = "retest"
        test._waitAndTouch("socialBtn.png", test_section)
        test._waitAndTouch("backBtn.png", test_section)
    time2 = datetime.now()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("testergamelion66@gmail.com", "dupa1212")
    msg['Subject'] = 'Koniec retestu. Wynik - ok. Czas: {}'.format((str(time2-time1))[:7])
    server.sendmail("testergamelion66@gmail.com", "mateusz.holz@huuugegames.com", msg.as_string())
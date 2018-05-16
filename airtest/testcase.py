import extended_airtest
from airtest.core.api import *
from airtest.core.device import *
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import sys

credentianals = ('testergamelion66@gmail.com', 'dupa1212')

automat = extended_airtest.airtestAutomation('3300fe50be2ca3e1', 'com.huuuge.stars.slots')
automat.runShellCommand('logcat -c')
######################################################################################
######################################TEST CASE#######################################
######################################################################################
automat.setTestSection('full_tutorial')
automat.waitAndTouch('allow-button-7')
automat.waitAndTouch('lang_ok', sleepTime = 40)
automat.waitAndTouch('profile_play', sleepTime = 15)
automat.waitAndTouch('tut_1', sleepTime = 5)
automat.waitAndTouch('tut_2', sleepTime = 5)
automat.waitAndTouch('tut_3', sleepTime = 5)
automat.waitAndTouch('tut_4', sleepTime = 5)
automat.waitAndTouch('tut_5', sleepTime = 25)
automat.waitAndTouch('tut_6', sleepTime = 7)
automat.setTestSection('clubs')

""" def deployTest(build = None, recur = False, dev = None, index=0):
        test_section = 'clubs'
        test._waitAndTouch('lobby_button.png', test_section)
        test._waitAndTouch('get_started.png', test_section)
        test._waitAndTouch('skip.png', test_section)
        test._waitAndTouch('dismiss_tooltips.png', test_section)
        test._waitAndTouch('create_club.png', test_section)
        test._waitAndTouch('random_club_symbol.png', test_section)
        test._waitAndTouch('club_name_input.png', test_section)
        text('automat{}'.format(index))
        test._waitAndTouch('club_desc_input.png', test_section)
        text('automat{}'.format(index))
        sleep(3)
        test._waitAndTouch('create_club_button.png', test_section)
        sleep(3)
        time2 = datetime.now()
        mailSubject = 'Koniec testu nr: {}. Czas wykonania: {}'.format((index), str((time2-time1))[:7])
        if index%10 == 0:
            test.sendMail(credentianals, subject = mailSubject)
    except Exception as exc:
        if build:
            sub = 'Tests failed. Build: {}'.format(build)
        else:
            sub = 'Tests failed.'
        #test.sendMail(credentianals, serialNo = dev.getprop('ro.serialno'), bodyTxt = str(exc), subject = sub, takeImage = True)
        if recur:
            deployTest(recur = True, dev = dev, index = index+1)
        else:
            dev.keyevent('KEYCODE_POWER')
            uninstall('com.huuuge.stars.slots')
    if recur:
        deployTest(recur = True, dev = dev, index = index+1) """
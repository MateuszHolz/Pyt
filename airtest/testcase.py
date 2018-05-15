import extended_airtest as test
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

def prepareDevice():
    try:
        dev = connect_device('android:///3300fe50be2ca3e1') # samsung galaxy a5
    except Exception:
        dev = connect_device('android:///3300fe50be2ca3e1') # samsung galaxy a5
    wake()
    return dev

def deployTest(build = None, recur = False, dev = None, index=0):
    try:
        if build:
            uninstall('com.huuuge.stars.slots')
            install(build)
        else:
            if dev.check_app('com.huuuge.stars.slots') == False:
                install(r'{}\builds\HuuugeStars-0.1.248-master-(4d73c26f241bf1efb26eba008adae91be768e129)-release.apk'.format(os.getcwd()))
            else:
                clear_app('com.huuuge.stars.slots')
                pass
        shell('logcat -c')
        time1 = datetime.now()
        start_app('com.huuuge.stars.slots')
        ######################################################################################
        ######################################TEST CASE#######################################
        ######################################################################################
        test_section = 'full_tutorial'
        test._waitAndTouch('allow-button-{}.png'.format(dev.getprop('ro.build.version.release')[0]), test_section)
        test._waitAndTouch('lang_ok.png', test_section)
        sleep(35)
        test._waitAndTouch('profile_play.png', test_section)
        sleep(10)
        test._waitAndTouch('tut_1.png', test_section)
        sleep(2)
        test._waitAndTouch('tut_2.png', test_section)
        sleep(2)
        test._waitAndTouch('tut_3.png', test_section)
        sleep(2)
        test._waitAndTouch('tut_4.png', test_section)
        sleep(2)
        test._waitAndTouch('tut_5.png', test_section)
        sleep(20)
        test._waitAndTouch('tut_6.png', test_section)
        sleep(5)
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
        deployTest(recur = True, dev = dev, index = index+1)


if __name__ == '__main__':
    device = prepareDevice()
    deployTest(recur = True, dev = device, index=15)
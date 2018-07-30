import extended_airtest
import threading

credentianals = ('testergamelion66@gmail.com', 'dupa1212')

def runTests(automat, curIndx = 0):
	automat.clearAppData()
	automat.runApp()
	automat.wait(2)
	automat.runShellCommand('logcat -c')
	automat.setTestSection('full_tutorial')
	automat.waitAndTouch('allow-button')
	automat.waitAndTouch('allow-button')
	automat.waitAndTouch('lang_eng')
	automat.waitAndTouch('lang_ok', sleepTime = 40)
	automat.waitAndTouch('accept_eula')
	automat.waitAndTouch('tut_1', sleepTime = 5)
	automat.waitAndTouch('tut_2', sleepTime = 5)
	automat.waitAndTouch('tut_3', sleepTime = 5)
	automat.waitAndTouch('tut_4', sleepTime = 5)
	automat.waitAndTouch('tut_5', sleepTime = 25)
	automat.waitAndTouch('tut_6', sleepTime = 7)
	automat.waitAndTouch('profile_play')
	automat.setTestSection('clubs')
	automat.waitAndTouch('lobby_button')
	automat.waitAndTouch('get_started')
	automat.waitAndTouch('skip')
	automat.waitAndTouch('dismiss_tooltips')
	automat.waitAndTouch('create_club')
	automat.waitAndTouch('random_club_symbol')
	automat.waitAndTouch('club_name_input')
	automat.type('kielbasa{}'.format(automat.getIndex()))
	automat.waitAndTouch('club_desc_input')
	automat.type('klub{}'.format(automat.getIndex()))
	automat.waitAndTouch('create_club_button')


aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')

runTests(automat = aut)

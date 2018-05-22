import extended_airtest
import threading

credentianals = ('testergamelion66@gmail.com', 'dupa1212')

def runTests(automat, curIndx = 0):
	try:
		automat.setIndex(curIndx)
		for i in range(100000):
			automat.clearAppData()
			automat.runApp()
			automat.runShellCommand('logcat -c')
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
			automat.waitAndTouch('lobby_button')
			automat.waitAndTouch('get_started')
			automat.waitAndTouch('skip')
			automat.waitAndTouch('dismiss_tooltips')
			automat.waitAndTouch('create_club')
			automat.waitAndTouch('random_club_symbol')
			automat.waitAndTouch('club_name_input')
			automat.type('klub{}'.format(automat.getIndex()))
			automat.waitAndTouch('club_desc_input')
			automat.type('klub{}'.format(automat.getIndex()))
			automat.waitAndTouch('create_club_button')
			automat.setIndex(automat.getIndex()+1)
	except Exception:
		automat.sendMail(auth = credentianals, subject = 'Error po probie {}'.format(automat.getIndex(mail = True)), bodyTxt = '{} {}'.format(automat.getCurrScreen(), automat.getCurrAction()))
		runTests(aut, automat.getIndex())


aut = extended_airtest.airtestAutomation('3300fe50be2ca3e1', 'com.huuuge.stars.slots')

runTests(automat = aut, curIndx = 16)
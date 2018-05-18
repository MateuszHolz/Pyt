import extended_airtest

credentianals = ('testergamelion66@gmail.com', 'dupa1212')

def runTests(automat):
	try:
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
		automat.type('club{}'.format(automat.getIndex()))
		automat.waitAndTouch('club_desc_input')
		automat.type('club{}'.format(automat.getIndex()))
		automat.waitAndTouch('create_club_button')
		automat.setIndex(automat.getIndex()+1)
		runTests(automat)
	except Exception:
		runTests(automat)


aut = extended_airtest.airtestAutomation('3300fe50be2ca3e1', 'com.huuuge.stars.slots')

runTests(aut)
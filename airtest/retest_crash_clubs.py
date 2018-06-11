import extended_airtest


def runTests(automat):
	for i in range(100):
		automat.setTestSection('clubs')
		automat.waitAndTouch('create_club')
		automat.waitAndTouch('random_club_symbol')
		automat.waitAndTouch('club_name_input')
		automat.type('retesastasasasd')
		automat.waitAndTouch('club_desc_input')
		automat.type('retesastasasasd')
		automat.waitAndTouch('create_club_button')
		automat.waitAndTouch('button_menu')
		automat.waitAndTouch('button_leave_current_club')
		automat.waitAndTouch('button_leave_club_yes')

aut = extended_airtest.airtestAutomation('3300fe50be2ca3e1', 'com.huuuge.stars.slots')

runTests(aut)
import extended_airtest

credentianals = ('testergamelion66@gmail.com', 'dupa1212')

def runTests(automat):
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
    automat.waitAndTouch('club_search_input_field')
    automat.type('hbhb')
    automat.wait(2)
    automat.waitAndTouch('club_record')
    automat.waitAndTouch('request_invitation')
    runTests(automat)

aut = extended_airtest.airtestAutomation('3300fe50be2ca3e1', 'com.huuuge.stars.slots')

try:
    runTests(aut)
except Exception:
    runTests(aut)
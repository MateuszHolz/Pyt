import extended_airtest

def runTests(automat):
    while True:
        try:
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
            automat.setTestSection('social')
            automat.waitAndTouch('social_button')
            automat.waitAndTouch('social_connect')
            automat.waitAndTouch('input_field')
            automat.type('1096')
            automat.waitAndTouch('submit')
        except:
            runTests(automat)


aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')

runTests(automat = aut)
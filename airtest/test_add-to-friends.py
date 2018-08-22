import extended_airtest
import testsuites

def runTests(automat):
    try:
        while True:
            automat.clearAppData()
            automat.runApp()
            automat.type('ad')
            automat.wait(2)
            automat.runShellCommand('logcat -c')
            testsuites.testTutorial(automat)
            testsuites.testSocial(aut, userId = '2203')
    except Exception:
        runTests(automat)

aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')

runTests(automat = aut)
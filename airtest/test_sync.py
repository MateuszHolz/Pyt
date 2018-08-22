import extended_airtest
import testsuites

def runTests(automat):
#    try:
        automat.clearAppData()
        automat.runApp()
        automat.type('ad')
        automat.wait(2)
        automat.runShellCommand
        d('logcat -c')
        testsuites.testTutorial(automat)
        automat.createTelnet(automat)
        #testsuites.testSocial(automat)
        #testsuites.testClubs(automat)
        testsuites.testLottery(automat)
        #testsuites.testNewsfeed(automat)

    #except Exception:
    #    automat.sendMail(subject = 'Sync Test, Section: {}, Status: Failed'.format(automat.getTestSection()))


aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')

runTests(automat = aut)
import extended_airtest
import testsuites

def runTests(automat):
    try:
        testsuites.testTutorial(automat, True)
        testsuites.testClubs(automat, True)
        testsuites.testSocial(automat, True)
        #testsuites.testLottery(automat, True) ## NOT READY YET
        testsuites.testNewsfeed(automat, True)
        testsuites.testLeaderboards(automat, True)
        automat.createTelnet(automat)
        automat.telnet.reachLevel(300, skipLobbyPopups = True)
        testsuites.seekForSlot(automat, 'wheel_of_wins', True)

    except Exception as ex:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Failed. Error: {}'.format(automat.getTestSection(), ex))


aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')

runTests(automat = aut)
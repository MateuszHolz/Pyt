import extended_airtest
import testsuites_menu

def runTests(automat):
    try:
        testsuites_menu.testTutorial(automat, True)
        automat.createTelnet(automat)        
        testsuites_menu.testClubs(automat, True)
        testsuites_menu.testSocial(automat, True)
        testsuites_menu.testLottery(automat, True)
        testsuites_menu.testNewsfeed(automat, True)
        testsuites_menu.testLeaderboards(automat, True)
        automat.telnet.reachLevel(100, skipLobbyPopups = True)
        testsuites_menu.seekAndEnterSlot(automat, 'wheel_of_wins', True)

    except Exception as ex:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Failed. Error: {}'.format(automat.getTestSection(), ex))


aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')

runTests(automat = aut)
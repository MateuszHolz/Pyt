import extended_airtest
import testsuites


def runTests(automat):
    testsuites.testTutorial(automat)
    automat.createTelnet(automat)
    automat.telnet.reachLevel(300, skipLobbyPopups = True)
    testsuites.seekForSlot(automat, 'wheel_of_wins')


aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')
runTests(automat = aut)
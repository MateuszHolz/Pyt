import extended_airtest
import testsuites


def runTests(automat):
    testsuites.testTutorial(automat)
    automat.createTelnet(automat)
    print('\n\nCURRENT LEVEL: ', automat.telnet.getLevel(), '\n\n')
    automat.telnet.reachLevel(100, skipLobbyPopups = True)





aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')
runTests(automat = aut)
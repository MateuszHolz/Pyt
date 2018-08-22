import extended_airtest
import testsuites_menu
import testsuites_slots


def runTests(automat):
    testsuites_menu.testTutorial(automat)
    automat.createTelnet(automat)
    automat.telnet.reachLevel(100, skipLobbyPopups = True)
    testsuites_menu.seekAndEnterSlot(automat, 'wheel_of_wins')
    testsuites_slots.wheel_of_wins(automat)


aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')
runTests(automat = aut)
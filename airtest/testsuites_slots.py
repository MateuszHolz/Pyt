def wheel_of_wins(automat):
    automat.setTestSection('wheel_of_wins')
    automat.waitAndTouch('spin_btn')
    for i in range(10):
        print('\n\n\n', automat.telnet.sendTelnetCommand('server game hugewin'), '\n\n\n')
        automat.waitAndTouch('spin_btn', sleepTime = 20)
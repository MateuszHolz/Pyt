import extended_airtest

def runTests(automat):
#    try:
        automat.clearAppData()
        automat.runApp()
        automat.wait(2)
        automat.runShellCommand('logcat -c')
        testTutorial(automat)
        automat.createTelnet(automat)
        testSocial(automat)
        testClubs(automat)
        testLottery(automat)
        testNewsfeed(automat)

    #except Exception:
    #    automat.sendMail(subject = 'Sync Test, Section: {}, Status: Failed'.format(automat.getTestSection()))

def testClubs(automat, sendMail = False):
    automat.setTestSection('clubs')
    automat.waitAndTouch('clubs_lobby_button')
    automat.waitAndTouch('ok_button')
    automat.waitAndTouch('skip_button')
    automat.waitAndTouch('dismiss_tooltips')
    automat.waitAndTouch('invites_tab')
    automat.waitAndTouch('create_club_button')
    automat.waitAndTouch('random_club_symbol')
    automat.waitAndTouch('club_name_input')
    automat.type('{}'[:9].format(automat.getCurrentTimestamp()))
    automat.waitAndTouch('club_desc_input')
    automat.type('Test Sync')
    automat.waitAndTouch('create_button')
    automat.waitAndTouch('donate_button')
    automat.waitAndTouch('donate2_button')
    automat.waitAndTouch('chat')
    automat.waitAndTouch('emots')
    automat.waitAndTouch('emots')
    automat.waitAndTouch('chat_type_msg')
    automat.type('dupa'*20)
    automat.waitAndTouch('chat_logs')
    automat.useDeviceBackButton()
    automat.waitAndTouch('club_wall_tab')
    automat.waitAndTouch('filters')
    automat.waitAndTouch('apply_filters')
    automat.waitAndTouch('club_wall_type_msg')
    automat.type('dupa'*20)
    automat.waitAndTouch('leaderboard_tab')
    automat.waitAndTouch('club_events_tab')
    automat.waitAndTouch('requests_tab')
    automat.waitAndTouch('options')
    automat.waitAndTouch('leave_club')
    automat.waitAndTouch('leave_club_confirm')
    automat.useDeviceBackButton()
    if sendMail:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Passed'.format(automat.getTestSection()))

def testTutorial(automat, sendMail = False):
    automat.setTestSection('tutorial')
    automat.waitAndTouch('allow-button')
    automat.waitAndTouch('allow-button')
    automat.waitAndTouch('lang_eng')
    automat.waitAndTouch('lang_ok', sleepTime = 30)
    automat.waitAndTouch('accept_eula')
    automat.waitAndTouch('tut_1', sleepTime = 6)
    automat.waitAndTouch('tut_2', sleepTime = 5)
    automat.waitAndTouch('tut_3', sleepTime = 5)
    automat.waitAndTouch('tut_4', sleepTime = 5)
    automat.waitAndTouch('tut_5', sleepTime = 25)
    automat.waitAndTouch('tut_6', sleepTime = 7)
    automat.waitAndTouch('profile_play')
    if sendMail:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Passed'.format(automat.getTestSection()))

def testSocial(automat, sendMail = False):
    automat.setTestSection('social')
    automat.waitAndTouch('social_lobby_button')
    automat.waitAndTouch('from_my_club')
    automat.waitAndTouch('join_club')
    automat.useDeviceBackButton()
    automat.waitAndTouch('social_connect')
    automat.waitAndTouch('input_field')
    automat.type('1')
    automat.waitAndTouch('submit')
    automat.waitAndTouch('ok_button')
    automat.waitAndTouch('shop_plus_button')
    automat.useDeviceBackButton()
    automat.waitAndTouch('back_top_left')
    if sendMail:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Passed'.format(automat.getTestSection()))

def testLottery(automat, sendMail = False):
    automat.setTestSection('lottery')
    automat.waitAndTouch('lobby_button')
    automat.waitAndTouch('try_lottery')
    automat.telnet.sendTelnetCommand('server lottery bronze 0') #make sure we win CHIPS
    automat.waitAndTouch('free_bronze', sleepTime = 5)
    automat.waitAndTouch('bronze_get')
    automat.waitAndTouch('iap_bronze_01', sleepTime = 5)
    automat.waitAndTouch('buy_gp', sleepTime = 12)
    automat.waitAndTouch('purchase_collect')
    automat.waitAndTouch('silver_get')
    automat.waitAndTouch('iap_silver_02', sleepTime = 5)
    automat.waitAndTouch('buy_gp', sleepTime = 12)
    automat.waitAndTouch('purchase_collect')
    automat.waitAndTouch('gold_get')
    automat.waitAndTouch('iap_gold_04', sleepTime = 5)
    automat.waitAndTouch('buy_gp', sleepTime = 12)
    automat.waitAndTouch('purchase_collect')
    automat.waitAndTouch('bronze_after_purchase', sleepTime = 5)
    automat.waitAndTouch('silver_after_purchase', sleepTime = 5)
    automat.waitAndTouch('gold_after_purchase', sleepTime = 5)
    automat.waitAndTouch('paytable')
    automat.useDeviceBackButton()
    automat.waitAndTouch('shop')
    automat.useDeviceBackButton()
    automat.useDeviceBackButton()
    if sendMail:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Passed'.format(automat.getTestSection()))

def testNewsfeed(automat, sendMail = False):
    automat.setTestSection('newsfeed')
    automat.waitAndTouch('newsfeed_lobby_button')
    automat.waitAndTouch('newsfeed_fb_connect')
    automat.useDeviceBackButton()
    automat.waitAndTouch('newsfeed_arrow_right')
    automat.waitAndTouch('newsfeed_rate')
    automat.useDeviceBackButton()
    automat.useDeviceBackButton()
    if sendMail:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Passed'.format(automat.getTestSection()))

def testLeaderboards(automat, sendMail = False):
    automat.setTestSection('leaderboards')
    automat.waitAndTouch('leaderboards_lobby_button')
    automat.waitAndTouch('leaderboards_famous_players_tab')
    automat.waitAndTouch('leaderboards_happy_players_tab')
    automat.waitAndTouch('leaderboards_slots_tab')

aut = extended_airtest.airtestAutomation('AQH0217A27000562', 'com.huuuge.stars.slots')

runTests(automat = aut)
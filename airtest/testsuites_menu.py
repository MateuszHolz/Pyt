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

def testSocial(automat, sendMail = False, userId = '1'):
    automat.setTestSection('social')
    automat.waitAndTouch('social_lobby_button')
    automat.waitAndTouch('from_my_club')
    automat.waitAndTouch('join_club')
    automat.useDeviceBackButton()
    automat.waitAndTouch('social_connect')
    automat.waitAndTouch('input_field')
    automat.type(userId)
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
    automat.telnet.setNextLotteryTicketSafe('bronze')
    automat.waitAndTouch('free_bronze', sleepTime = 5)
    automat.waitAndTouch('bronze_get')
    automat.waitAndTouch('iap_bronze_01', sleepTime = 5)
    automat.waitAndTouch('buy_gp', sleepTime = 15)
    automat.waitAndTouch('purchase_collect')
    automat.waitAndTouch('silver_get')
    automat.waitAndTouch('iap_silver_02', sleepTime = 5)
    automat.waitAndTouch('buy_gp', sleepTime = 15)
    automat.waitAndTouch('purchase_collect')
    automat.waitAndTouch('gold_get')
    automat.waitAndTouch('iap_gold_04', sleepTime = 5)
    automat.waitAndTouch('buy_gp', sleepTime = 15)
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
    automat.swipeToDirection('up', 'mid', 1)
    automat.waitAndTouch('leaderboards_show_more')
    automat.waitAndTouch('leaderboards_most_winnings_yesterday')
    automat.useDeviceBackButton()
    automat.useDeviceBackButton()
    if sendMail:
        automat.sendMail(subject = 'Sync Test, Section: {}, Status: Passed'.format(automat.getTestSection()))

def seekAndEnterSlot(automat, slotScreen, sendMail = False):
    automat.setTestSection('lobby')
    automat.telnet.sendTelnetCommand('disconnect')
    automat.swipeRightUntil(slotScreen)
    automat.waitAndTouch(slotScreen)
    automat.waitAndTouch(slotScreen+'_rss_beginner')
    automat.wait(10)
    if sendMail:
        automat.sendMail(subject = 'Sync Test, Section: {}, SeekForSlot, Slot: {}, Status: Passed'.format(automat.getTestSection(), slotScreen))

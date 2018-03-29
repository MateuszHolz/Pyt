import extended_airtest as test
from airtest.core.api import *
from airtest.core.device import *

if __name__ == "__main__":
    test_section = ""
    dev = connect_device("android:///")
    screenRes = dev.get_display_info()['height'], dev.get_display_info()['width']
    posContainer = test.posContainer(screenRes)
    wake()
    if dev.check_app("com.huuuge.stars.slots") == False:
        install(r"{}\builds\HuuugeStars-0.1.248-master-(4d73c26f241bf1efb26eba008adae91be768e129)-release.apk".format(os.getcwd()))
    else:
        clear_app("com.huuuge.stars.slots")
        pass
    start_app("com.huuuge.stars.slots")
    test_section = "age_confirm"
    test._waitAndTouch("allow-button-{}.png".format(dev.getprop("ro.build.version.release")[0]), test_section, True, posContainer)
    test._waitAndTouch("green-ok.png", test_section, True, posContainer)
    test._waitAndTouch("day-1.png", test_section, True, posContainer)
    test._waitAndTouch("day-3.png", test_section, True, posContainer)
    test._waitAndTouch("month-jan.png", test_section, True, posContainer)
    test._waitAndTouch("month-mar.png", test_section, True, posContainer)
    test._waitAndTouch("year-2010.png", test_section, True, posContainer)
    swipePoint1=exists(test.constructTemplate("age-confirm-year-2007.png", test_section))
    swipePoint2=exists(test.constructTemplate("age-confirm-year-2013.png", test_section))
    for j in range(2):
        test._swipe(swipePoint1, swipePoint2, "points", test_section)
        sleep(2.0)
    clear_app("com.huuuge.stars.slots")
    with open('Positions_{}x{}.txt'.format(screenRes[0], screenRes[1]), 'w') as f:
        for key, value in posContainer.getPosContainer().items():
            f.write("{}, {}\n".format(key, value))
    #touch(swipePoint1)
    #sleep(3.0)
    #_waitAndTouch("green-continue.png")
    #sleep(10.0)
    #test_section = "profile"
    #_takeScrnShot("Lobby.png")
    #uninstall("com.huuuge.stars.slots")
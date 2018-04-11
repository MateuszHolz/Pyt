import extended_airtest as test
from airtest.core.api import *
from airtest.core.device import *

if __name__ == "__main__":
    test_section = ""
    dev = connect_device("android:///")
    wake()
    sleep(5)
    if dev.check_app("com.huuuge.stars.slots") == False:
        install(r"{}\builds\HuuugeStars-0.1.248-master-(4d73c26f241bf1efb26eba008adae91be768e129)-release.apk".format(os.getcwd()))
    else:
        clear_app("com.huuuge.stars.slots")
        pass
    
    for i in range(50):
        start_app("com.huuuge.stars.slots")
        test_section = "age_confirm"
        #test._waitAndTouch("allow-button-{}.png".format(dev.getprop("ro.build.version.release")[0]), test_section)
        test._waitAndTouch("green-ok.png", test_section)
        test._waitAndTouch("year-2010.png", test_section)
        swipePoint1=exists(test.constructTemplate("age-confirm-year-2007.png", test_section))
        swipePoint2=exists(test.constructTemplate("age-confirm-year-2013.png", test_section))
        for j in range(3):
            test._swipe(swipePoint1, swipePoint2, "points", test_section)
            sleep(1.0)
        years = ["1999", "1997", "1995", "1993", "1991", "1989"]
        sleep(2.0)
        for k in years:
            if exists(test.constructTemplate("{}.png".format(k), test_section)):
                test._waitAndTouch("{}.png".format(k), test_section)
                break
        sleep(3.0)
        test._waitAndTouch("green-continue.png", test_section)
        test_section = "tutorial"
        sleep(2.0)
        test._waitAndTouch("profile_play.png", test_section)
        test._waitAndTouch("tap_to_spin.png", test_section)
        sleep(2.0)
        test._waitAndTouch("tap_to_set_bet.png", test_section)
        test._waitAndTouch("tap_to_spin.png", test_section)
        test._waitAndTouch("spin_again.png", test_section)
        test._waitAndTouch("last_spin.png", test_section)
        sleep(22.0)
        test._waitAndTouch("continue_after_tut.png", test_section)
        test_section = "social"
        test._waitAndTouch("social_button.png", test_section)
        test._waitAndTouch("social_connect.png", test_section)
        test._waitAndTouch("input_field.png", test_section)
        text("933")
        sleep(2.0)
        test._waitAndTouch("submit.png", test_section)
        clear_app("com.huuuge.stars.slots")
import os

from airtest.core.api import *

test_section = ""

def constructTemplate(file):
    return Template(r"{}\testsc\{}\{}".format(os.getcwd(), test_section, file))

def _waitAndTouch(file):
    touch(wait(constructTemplate(file), interval = 1))
    sleep(1)

def _swipe(startPoint, endPoint, option):
    if option == "files":
        swipe(v1 = constructTemplate(startPoint), v2 = constructTemplate(endPoint))
    elif option == "points":
        swipe(v1 = startPoint, v2 = endPoint)

def _takeScrnShot(filename):
    snapshot(r"{}\output\{}".format(os.getcwd(), filename))

if __name__ == "__main__":
    test_section = ""
    connect_device("android:///")
    install(r"{}\builds\HuuugeStars-0.1.248-master-(4d73c26f241bf1efb26eba008adae91be768e129)-release.apk".format(os.getcwd()))
    start_app("com.huuuge.stars.slots")
    test_section = "age_confirm"
    _waitAndTouch("allow-button.png")
    _waitAndTouch("green-ok.png")
    _waitAndTouch("day-1.png")
    _waitAndTouch("day-3.png")
    _waitAndTouch("month-jan.png")
    _waitAndTouch("month-mar.png")
    _waitAndTouch("year-2010.png")
    swipePoint1=exists(constructTemplate("age-confirm-year-2007.png"))
    swipePoint2=exists(constructTemplate("age-confirm-year-2013.png"))
    for i in range(2):
        _swipe(swipePoint1, swipePoint2, "points")
        sleep(3.0)
    touch(swipePoint1)
    sleep(3.0)
    _waitAndTouch("green-continue.png")
    sleep(10.0)
    test_section = "profile"
    _takeScrnShot("Lobby.png")
    uninstall("com.huuuge.stars.slots")
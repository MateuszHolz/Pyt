import os

from airtest.core.api import *

def constructTemplate(file):
    return Template(r"{}\testsc\{}".format(os.getcwd(), file))

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

connect_device("ios:///")
#r"{}\builds\HuuugeStars-0.1.239-master-(c31644a12b3cd5d5d55a83dd1017476243fa2dfb)-ad-hoc.ipa".format(os.getcwd())
install("com.huuuge.stars.slots")
start_app("com.huuuge.stars.slots")
_waitAndTouch("allow_button.png")
_waitAndTouch("ok_bigger.png")
_waitAndTouch("age_confirm_day.png")
_waitAndTouch("age_confirm_3.png")
_waitAndTouch("age_confirm_month.png")
_waitAndTouch("age_confirm_mar.png")
_waitAndTouch("age_confirm_year.png")
swipePoint1=exists(constructTemplate("age_confirm_year_swipe_start.png"))
swipePoint2=exists(constructTemplate("age_confirm_year_swipe_stop.png"))
for i in range(2):
    _swipe(swipePoint1, swipePoint2, "points")
    sleep(3.0)
touch(swipePoint1)
sleep(3.0)
_waitAndTouch("age_green_continue.png")
sleep(10.0)
_takeScrnShot("Lobby.png")
uninstall("com.huuuge.stars.slots")
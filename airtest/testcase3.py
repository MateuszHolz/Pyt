import extended_airtest as ext
from airtest.core.api import *
from airtest.core.device import *

connect_device("android:///")
test_section = "retest"
for i in range(100):
    ext._waitAndTouch("socialBtn.png", test_section)
    ext._waitAndTouch("backBtn.png", test_section)


import extended_airtest as test
from airtest.core.api import *
from airtest.core.device import *

if __name__ == "__main__":
    test_section = "age_confirm"
    dev = connect_device("android:///")
    screenRes = dev.get_display_info()['height'], dev.get_display_info()['width']
    print(screenRes)
    test._waitAndTouch("testvip.png", test_section)
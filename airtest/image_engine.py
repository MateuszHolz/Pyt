import cv2
import numpy as np
from matplotlib import pyplot as plt


def getScreenshotFromDevice(adb):
    raise NotImplementedError


def isScreenVisible(img, template, threshold):
    img_rgb = cv2.imread(img)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    if len(loc[0]) < 1:
        return False
    else:
        return loc[0][0]+w/2, loc[1][0]+h/2

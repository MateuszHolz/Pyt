import cv2
import numpy
import urllib.request

fbid = "100000768536495"

def imgFromUrl(url):
    imageFromUrl = urllib.request.urlopen(url)
    image = numpy.asarray(bytearray(imageFromUrl.read()), dtype="uint8")
    return cv2.imdecode(image, cv2.IMREAD_COLOR)
def createFbUrl(id):
    return imgFromUrl("https://graph.facebook.com/{}/picture?type=large".format(id))

cv2.imshow("Test fb", createFbUrl(fbid))
cv2.waitKey(0)
cv2.destroyAllWindows()

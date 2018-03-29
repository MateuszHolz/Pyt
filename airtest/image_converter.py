import cv2
from airtest.core.api import *
import os
import extended_airtest as test


class imageConverter():
	def __init__(self, pathToImage, desiredSize):
		self.image = cv2.imread(pathToImage, 1)
		self.desiredSize = desiredSize
		self.temporaryFile = None
		self.newImage = None
	
	def getTemplateOfFile(self):
		tempDir = r'{}\tempDir'.format(os.getcwd())
		print("Temp Dir #1 = {}".format(tempDir))
		try:
			os.listdir(tempDir)
		except FileNotFoundError:
			os.mkdir(tempDir)
		
		self.temporaryFile = r'{}\temp.png'.format(tempDir)

		print(self.temporaryFile)
		
		self.newImage = cv2.resize(self.image, (self.desiredSize[0], self.desiredSize[1]), interpolation = cv2.INTER_AREA)

		cv2.imwrite(self.temporaryFile, self.newImage)

		return test.constructTemplate(self.temporaryFile)


imageConverter = imageConverter(r'C:\Users\mho\Desktop\Pyt\airtest\initial_profile_tap_to_change_avatar.png', (1280, 720))
print(imageConverter.getTemplateOfFile())

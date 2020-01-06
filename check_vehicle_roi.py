# The MIT License
#
# Copyright (c) Ironyun, Inc. http://www.ironyun.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import requests
import json
import urllib.request
import os
import sys
import logging

AINVR_ADDRESS = "http://AINVR_IP"
USERNAME = "username"
PASSWORD = "password"
OBJECT_TARGET = ['car']

class AINVR_API:
	def __init__(self):
		# setting for AINVR
		self.address = AINVR_ADDRESS
		self.username = USERNAME
		self.password = PASSWORD
		self.apiList = {"auth": "/ainvr/api/auth",
						"getCameraDetail": "/ainvr/api/cameras/{cameraId}",
						"createSnapshot": "/ainvr/api/cameras/snapshot",
						"detectObjects": "/ainvr/api/detection/objects",
						"getRoiDetail": "/ainvr/api/rois/{roiId}",
						}
		self.token = None
		self.getToken()

	def doReq(self, requestFunc, addr, token=None, **kwargs):

		"""
		We define unified doReq function to access the API and to handle errors in one place.
		:param requestFunc:  one of the function from requests lib, e.g.: requests.get or requests.post
		:param addr: API full URL
		:param kwargs: additional arguments to pass to the requestFunc
		:param token: if not null, pass it as a security header, used for request authorization
		:return: returns the same object as requestFunc or raise an error
		"""

		# If token is presented we modify kwargs accordingly
		if token:
			if 'headers' in kwargs:
				# We use deepcopy to not modify the original headers argument
				kwargs['headers'] = copy.deepcopy(kwargs['headers'])
				kwargs['headers']["X-Auth-Token"] = token
			else:
				kwargs['headers'] = {"X-Auth-Token": token}

		logger.debug("Issuing {} request to {} with params: {}".format(requestFunc.__name__, addr, kwargs))
		r = requestFunc(addr, **kwargs)
		try:
			r.raise_for_status()
		except Exception as e:
			logger.error('Exception while accessing {0}'.format(addr), exc_info=True)
			if r.text:
				logger.error('Reply from server: ' + r.text, exc_info=True)
			raise e
		return r

	def getToken(self):
		# print("Doing authentication...")
		cred = {"username": self.username, "password": self.password}
		res = self.doReq(requests.post, self.address + self.apiList['auth'], json=cred, verify=False)
		self.token = res.json()['token']
		# print("Token = " + str(self.token))
		
	def getCameraDetail(self, cameraId):
		try:
			res = self.doReq(requests.get, self.address + self.apiList['getCameraDetail'].format(cameraId=cameraId), self.token, verify=False)
		except Exception as e:
			logger.error(e, exc_info=True)
			# get AI-NVR session key
			self.getToken()
			res = self.doReq(requests.get, self.address + self.apiList['getCameraDetail'].format(cameraId=cameraId), self.token, verify=False)
		return res.json()

	def createSnapshot(self, payload):
		try:
			res = self.doReq(requests.post, self.address + self.apiList['createSnapshot'], self.token, verify=False, json=payload)
		except Exception as e:
			logger.error(e, exc_info=True)
			# get AI-NVR session key
			self.getToken()
			res = self.doReq(requests.post, self.address + self.apiList['createSnapshot'], self.token, verify=False, json=payload)
		return res.text

	def detectObjects(self, payload):
		try:
			res = self.doReq(requests.post, self.address + self.apiList['detectObjects'], self.token, verify=False, files=payload)
		except Exception as e:
			logger.error(e, exc_info=True)
			# get AI-NVR session key
			self.getToken()
			res = self.doReq(requests.post, self.address + self.apiList['detectObjects'], self.token, verify=False, files=payload)
		return res.json()

	def getRoiDetail(self, roiId):
		try:
			res = self.doReq(requests.get, self.address + self.apiList['getRoiDetail'].format(roiId=roiId), self.token, verify=False)
		except Exception as e:
			logger.error(e, exc_info=True)
			# get AI-NVR session key
			self.getToken()
			res = self.doReq(requests.get, self.address + self.apiList['getRoiDetail'].format(roiId=roiId), self.token, verify=False)
		return res.json()

class BOUNDING_BOX:
	def __init__(self, objectType, x, y, w, h, confidence, properties):
		self.objectType = objectType
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.confidence = confidence
		self.properties = properties
	
	def __str__(self):
		return "objectType="+self.objectType+", confidence="+str(self.confidence)+", ["+str(self.x)+","+str(self.y)+","+str(self.w)+","+str(self.h)+"]"

class ROI:
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def __str__(self):
		return "["+str(self.x)+","+str(self.y)+","+str(self.w)+","+str(self.h)+"]"

def userInput():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--cameraId', help='Camera ID', type=int, required=True)
	parser.add_argument('-r', '--roiId', help='ROI ID', type=int, required=True)
	args = parser.parse_args()
	return args

if __name__ == "__main__":
	# define logger
	logger = logging.getLogger()
	logger.setLevel(logging.INFO) # set DEBUG to get more information
	logger.addHandler(logging.StreamHandler())

	# get input and init classes
	args = userInput()
	ainvrAPI = AINVR_API()

	# define object target
	objectTarget = OBJECT_TARGET

	try:
		# get camera info by camera id
		camera = ainvrAPI.getCameraDetail(args.cameraId)
		logger.debug("streamUrl: " + camera['streamUrl'])
		
		# get snapshot and save by stream url
		snapshot = ainvrAPI.createSnapshot({'streamUrl': camera['streamUrl']})
		logger.debug("snapshot: " + snapshot)
		urllib.request.urlretrieve(snapshot, "temp.jpg")

		# get objects from detected image
		file = {'file': open("temp.jpg", "rb")}
		objects = ainvrAPI.detectObjects(file)
		logger.debug("objects: " + json.dumps(objects))

		# prepare object list with bounding box
		objectList = []
		for object in objects:
			# check if object's type is within object target
			if object['objectType'] in objectTarget:
				objectList.append(BOUNDING_BOX(object['objectType'], object['x'], object['y'], object['w'], object['h'], object['confidence'], object['properties']))
		
		# check object in object list
		for object in objectList:
			logger.debug("object: " + str(object))

		# get roi info by roi id
		roi = ainvrAPI.getRoiDetail(args.roiId)
		logger.debug("roi region: " + roi['region'])
		regions = json.loads(roi['region'])

		# prepare roi
		coordinates = regions[0]['contour']
		minX = min(coordinate['x'] for coordinate in coordinates)
		minY = min(coordinate['y'] for coordinate in coordinates)
		maxX = max(coordinate['x'] for coordinate in coordinates)
		maxY = max(coordinate['y'] for coordinate in coordinates)
		width = maxX - minX
		height = maxY - minY
		roi = ROI(minX, minY, width, height)

		# check if object target is in roi
		result = False
		for object in objectList:
			centerX = object.x + (object.w / 2)
			centerY = object.y + (object.h / 2)
			
			logger.info('----------')
			logger.info("objectType: " + object.objectType)
			logger.info("centerX: " + str(centerX))
			logger.info("centerY: " + str(centerY))
			if (roi.x <= centerX <= (roi.x + roi.w)) and (roi.y <= centerY <= (roi.y + roi.h)):
				result = True
				logger.info("the object is in the roi")

		logger.info('==========')
		logger.info("roi_minX: " + str(roi.x))
		logger.info("roi_maxX: " + str(roi.x + roi.w))
		logger.info("roi_minY: " + str(roi.y))
		logger.info("roi_maxY: " + str(roi.y + roi.h))
		logger.info('==========')
		logger.info("result: " + str(result))

	except Exception as e:
		logger.error(e, exc_info=True)
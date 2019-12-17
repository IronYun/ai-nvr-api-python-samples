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

import requests
import json

AINVR_ADDRESS = "http://172.16.22.104"
AUTH_API = "/ainvr/api/auth"
DETECTION_API = "/ainvr/api/detection/objects"
FACIAL_DETECTION_API = "/ainvr/api/face"
FACIAL_TARGET_KEY_API = "/ainvr/api/face/keys"
FILENAME = "person.jpg"
USERNAME = "developer"
PASSWORD = "p@ssWord"

if __name__ == "__main__":
    cred = {"username": USERNAME, "password": PASSWORD}
    token_r = requests.post(AINVR_ADDRESS + AUTH_API, json=cred, verify=False)
    apikey = token_r.json()['token']

    with open(FILENAME, "rb") as f:
        files_form = {"file": f}
        headers = {"X-Auth-Token": apikey}
        response = requests.post(AINVR_ADDRESS + FACIAL_DETECTION_API, files=files_form, headers=headers, verify=False)
        descriptor = response.json()[0]['descriptor']
        confidence = response.json()[0]['confidence']
        age = response.json()[0]['age']
        gender = response.json()[0]['gender']
                
        response = requests.get(AINVR_ADDRESS + FACIAL_TARGET_KEY_API + "?descriptor=" + descriptor + "&limit=1", headers=headers, verify=False)        
        name = response.json()[0]['faceTarget']['name']
                
        print(name)
        print(confidence)
        print(age)
        print(gender)
      
        
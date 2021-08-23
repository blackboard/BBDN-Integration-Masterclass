import json
from cachetools import TTLCache
import requests
import datetime
import time
import ssl
import sys
import os
import urllib.parse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Config
import Config as config


class RestController():
    target_url = ''

    def __init__(self, token):

        self.HEADER = {
            "Authorization" : f"Bearer {token}"
        }

        self.target_url = config.tool_config['LEARN_REST_URL']

        if config.tool_config['VERIFY_CERTS'] == 'True':
            self.verify_certs = True
        else:
            self.verify_certs = False

    def getUser(self, uuid):
        OAUTH_URL = f"https://{self.target_url}/learn/api/public/v1/users/uuid:{uuid}?fields=userName"
        
        r = requests.get(OAUTH_URL, headers=self.HEADER, verify=self.verify_certs)

        if r.status_code == 200:
            return json.loads(r.text)
    
    def getCourse(self, uuid):
        OAUTH_URL = f"https://{self.target_url}/learn/api/public/v3/courses/uuid:{uuid}?fields=id,externalId"
        
        r = requests.get(OAUTH_URL, headers=self.HEADER, verify=self.verify_certs)

        if r.status_code == 200:
            return json.loads(r.text)

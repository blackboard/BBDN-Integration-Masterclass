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
        return
    
    def getCourse(self, uuid):
        return
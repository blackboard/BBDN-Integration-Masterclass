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


class RestAuthController():
    target_url = ''

    def __init__(self, authcode=None):

        self.KEY = config.tool_config['LEARN_REST_KEY']
        self.SECRET = config.tool_config['LEARN_REST_SECRET']

        if authcode is not None:
            self.CREDENTIALS = 'authorization_code'
        else:
            self.CREDENTIALS = 'client_credentials'
        self.PAYLOAD = {
            'grant_type': self.CREDENTIALS
        }
        self.TOKEN = None
        self.target_url = config.tool_config['LEARN_REST_URL']

        self.app_url = config.tool_config['APP_URL']

        self.authcode = authcode

        self.EXPIRES_AT = ''

        if config.tool_config['VERIFY_CERTS'] == 'True':
            self.verify_certs = True
        else:
            self.verify_certs = False

        self.cache = None

        self.uuid = None

    def getKey(self):
        return self.KEY

    def getSecret(self):
        return self.SECRET

    def setToken(self):
        try:
            if self.cache != None:
                token = self.cache['token']
            else:
                self.requestToken()
        except KeyError:
            self.requestToken()

    def requestToken(self):
        OAUTH_URL = f"https://{self.target_url}/learn/api/public/v1/oauth2/token"
        
        if self.CREDENTIALS == 'authorization_code':
            OAUTH_URL += f"?code={self.authcode}&redirect_uri={self.app_url}/authcode/"

        # Authenticate
        print("[auth:setToken] POST Request URL: " + OAUTH_URL)
        print("[auth:setToken] JSON Payload: \n" + json.dumps(self.PAYLOAD, indent=4, separators=(',', ': ')))

        r = requests.post(OAUTH_URL, data=self.PAYLOAD, auth=(self.KEY, self.SECRET), verify=self.verify_certs)

        print("[auth:setToken()] STATUS CODE: " + str(r.status_code))
        # strip quotes from result for better dumps
        res = json.loads(r.text)
        print("[auth:setToken()] RESPONSE: \n" + json.dumps(res, indent=4, separators=(',', ': ')))

        if r.status_code == 200:
            parsed_json = json.loads(r.text)

            self.cache = TTLCache(maxsize=1, ttl=parsed_json['expires_in'])

            self.cache['token'] = parsed_json['access_token']
            
            if 'uuid' in parsed_json:
                self.uuid = parsed_json['user_id']

            print("[auth:setToken()] TOKEN: " + self.getToken())

        else:
            print("[auth:setToken()] ERROR")

    def getToken(self):
        try:
            token = self.cache['token']

            return token
        except TypeError:
            self.setToken()

            return self.cache['token']
        except KeyError:
            self.setToken()

            return self.cache['token']

    def getUuid(self):
        return (self.uuid)
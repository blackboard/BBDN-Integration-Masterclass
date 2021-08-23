import os
import pprint
import urllib
import uuid
from tempfile import mkdtemp

from flask import Flask, render_template, jsonify
from flask import redirect, request
from flask_caching import Cache

from pylti1p3.contrib.flask import FlaskMessageLaunch, FlaskOIDCLogin, FlaskRequest, FlaskCacheDataStorage
from pylti1p3.tool_config import ToolConfJsonFile

import Config as config

import RestController
import RestAuthController

## TODO
PAGE_TITLE = 'Title'


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask('LTI-Workshop', template_folder='templates', static_folder='static')

app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config.from_mapping(config.tool_config)

cache = Cache(app)

class ExtendedFlaskMessageLaunch(FlaskMessageLaunch):

    def validate_nonce(self):
        """
        Probably it is bug on "https://lti-ri.imsglobal.org":
        site passes invalid "nonce" value during deep links launch.
        Because of this in case of iss == http://imsglobal.org just skip nonce validation.
        """
        iss = self.get_iss()
        deep_link_launch = self.is_deep_link_launch()
        if iss == "http://imsglobal.org" and deep_link_launch:
            return self
        return super(ExtendedFlaskMessageLaunch, self).validate_nonce()


def get_lti_config_path():
    return os.path.join(app.root_path, 'lti.json')


def get_launch_data_storage():
    return FlaskCacheDataStorage(cache)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('helloworld.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    return

@app.route('/launch/', methods=['HEAD', 'GET', 'POST'])
def launch():
    return

@app.route('/jwks/', methods=['GET'])
def get_jwks():
    return

if __name__ == '__main__':
    restAuthController = None
    app.run(host='0.0.0.0', port=5000)

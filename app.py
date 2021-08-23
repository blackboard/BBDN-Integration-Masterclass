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
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    launch_data_storage = get_launch_data_storage()

    flask_request = FlaskRequest()
    target_link_uri = flask_request.get_param('target_link_uri')

    if not target_link_uri:
        raise Exception('Missing "target_link_uri" param')

    oidc_login = FlaskOIDCLogin(flask_request, tool_conf, launch_data_storage=launch_data_storage)
    return oidc_login \
        .enable_check_cookies() \
        .redirect(target_link_uri)


@app.route('/launch/', methods=['HEAD', 'GET', 'POST'])
def launch():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch(flask_request, tool_conf, launch_data_storage=launch_data_storage)
    message_launch_data = message_launch.get_launch_data()
    pprint.pprint(message_launch_data)
    
    restAuthController = RestAuthController.RestAuthController()
    restAuthController.setToken()
    token = restAuthController.getToken()

    restController = RestController.RestController(token)
    user = restController.getUser(message_launch_data["sub"])
    course = restController.getCourse(message_launch_data["https://purl.imsglobal.org/spec/lti/claim/context"]["id"])

    tp_kwargs = {
        "username": user['userName'],
        "user_uuid": message_launch_data["sub"],
        "user_batch_uid": message_launch_data["https://purl.imsglobal.org/spec/lti/claim/lis"]["person_sourcedid"],
        "course_id": course['id'],
        "course_title": message_launch_data["https://purl.imsglobal.org/spec/lti/claim/context"]["title"],
        "course_uuid": message_launch_data["https://purl.imsglobal.org/spec/lti/claim/context"]["id"],
        "course_batch_uid": course['externalId'] 
    }

    return render_template('index.html', **tp_kwargs)

@app.route('/jwks/', methods=['GET'])
def get_jwks():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    return jsonify({'keys': tool_conf.get_jwks()})

if __name__ == '__main__':
    restAuthController = None
    app.run(host='0.0.0.0', port=5000)

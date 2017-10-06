#!/usr/bin/env python

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

import logging
import os.path
import webapp2

from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError


from utility import BaseHandler
from utility import Utility


class FacebookHandler(BaseHandler):
    APP_ID = "288727298296356"
    APP_SECRET = "c316f5bcb0b28c1012cd6ce759af320e"
    GRAPH_API_ME_URI="https://graph.facebook.com/v2.5/me?fields=email&access_token="
    REDIRECT_URL = 'http://hello12345.test.com/'
    GRAPH_API_AUTH_URI = ('https://graph.facebook.com/v2.2/oauth/'
                                   + 'access_token?client_id=' + APP_ID + '&redirect_uri='
                                   + REDIRECT_URL + '&client_secret=' +APP_SECRET + '&code=')


    
    def get(self):
        self.render_template('signup.html')

        if self.request.get('code') :
            
            auth_code = self.request.get('code') 
            access_token_resp = Utility.get_json_response( FacebookHandler.GRAPH_API_AUTH_URI + auth_code)
            profile_resp = Utility.get_json_response(FacebookHandler.GRAPH_API_ME_URI + access_token_resp["access_token"])

            user_name = profile_resp['email'];
            email = profile_resp['email'];
            name = profile_resp['name'];
            last_name = profile_resp['lastname'];

            unique_properties = ['email_address']
            user_data = self.user_model.create_user(user_name,
                                                    unique_properties,
                                                    email_address=email, name=name,
                                                    last_name=last_name, verified=True)
            if not user_data[0]:  # user_data is a tuple
                self.display_message('Unable to create user for email %s because of \
                duplicate keys %s' % (user_name, user_data[1]))
                return
            self.auth.set_session(
            self.auth.store.user_to_dict(user_data), remember=True)
            self.display_message('User email address has been verified.')

    def post(self):
        user_name = self.request.get('username')
        email = self.request.get('email')
        name = self.request.get('name')
        password = self.request.get('password')
        last_name = self.request.get('lastname')

        unique_properties = ['email_address']
        user_data = self.user_model.create_user(user_name,
                                                unique_properties,
                                                email_address=email, name=name, password_raw=password,
                                                last_name=last_name, verified=False)
        if not user_data[0]:  # user_data is a tuple
            self.display_message('Unable to create user for email %s because of \
        duplicate keys %s' % (user_name, user_data[1]))
            return

        user = user_data[1]
        user_id = user.get_id()

        token = self.user_model.create_signup_token(user_id)

        verification_url = self.uri_for('verification', type='v', user_id=user_id,
                                        signup_token=token, _full=True)

        msg = 'Send an email to user in order to verify their address. \
          They will be able to do so by visiting <a href="{url}">{url}</a>'

        self.display_message(msg.format(url=verification_url))


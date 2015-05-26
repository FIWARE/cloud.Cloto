#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
__author__ = 'gjp'
from keystoneclient.exceptions import AuthorizationFailure, Unauthorized, InternalServerError
from keystoneclient.exceptions import ClientException as KeystoneClientException
from keystoneclient.exceptions import ConnectionRefused as KeystoneConnectionRefused
from cloto.models import TokenModel
import json
import requests
import logging as logger
from cloto.constants import ACCEPT_HEADER, JSON_TYPE, X_AUTH_TOKEN_HEADER, TOKENS_PATH, DEFAULT_REQUEST_TIMEOUT,\
    X_SUBJECT_TOKEN_HEADER, TOKENS_PATH_V3


class AuthorizationManager():
    """This class provides methods to manage authorization.
    """
    myClient = None
    client = requests
    session = None

    def generate_session(self, username, password, tenant_id, tenant_name, user_domain_name, auth_api, url):
        """
        Init the variables related to authorization, needed to execute tests
        :return: The auth token retrieved
        """

        cred_kwargs = {
            'auth_url': url,
            'username': username,
            'password': password
        }

        # Currently, both v2 and v3 Identity API versions are supported
        if auth_api == 'v2.0':
            cred_kwargs['tenant_name'] = tenant_name
        elif auth_api == 'v3':
            cred_kwargs['user_domain_name'] = user_domain_name

        # Instantiate a Password object
        try:
            identity_package = 'keystoneclient.auth.identity.%s' % auth_api.replace('.0', '')
            identity_module = __import__(identity_package, fromlist=['Password'])
            password_class = getattr(identity_module, 'Password')
            logger.debug("Authentication with %s", password_class)
            credentials = password_class(**cred_kwargs)
        except (ImportError, AttributeError) as e:
                raise e
        # Get auth token
        logger.debug("Getting auth token for tenant %s...", tenant_id)
        print cred_kwargs
        try:
            auth_sess = self.session.Session(auth=credentials, timeout=DEFAULT_REQUEST_TIMEOUT)
            auth_token = auth_sess.get_token()
            print("Admin token generated:" + auth_token)

        except (KeystoneClientException, KeystoneConnectionRefused) as e:
            logger.error("No auth token (%s)", e.message)
            print e.message
            raise(e)

        return auth_token

    def checkToken(self, admin_token, token, tenant_id, url, auth_api):
        """checks if a token is valid against a url using an admin token."""
        logger.info("Starting Authentication of token %s " % token)
        try:
            if not token:
                raise Unauthorized("Token is empty")
            auth_result = self.get_info_token(url, admin_token, token, auth_api)
            if auth_result:
                if tenant_id == auth_result.tenant["id"]:
                    logger.info('The token is valid')
                else:
                    logger.error("TenantId %s " % tenant_id)
                    logger.error("Token TenantId %s " % auth_result.tenant["id"])
                    raise Unauthorized("Token is not valid for specified tenant %s" % tenant_id)
        except Unauthorized as unauth:
            logger.error(unauth)
            raise unauth
        except InternalServerError as internalError:
            raise AuthorizationFailure("Token could not have enough permissions to access tenant: %s" % tenant_id)
        except Exception as ex:
            raise ex

    def get_info_token(self, url, admin_token, token, auth_api):

        if auth_api == 'v2.0':
            headers = {ACCEPT_HEADER: JSON_TYPE, X_AUTH_TOKEN_HEADER: admin_token}
            r = self.client.get(url + "/" + TOKENS_PATH + token, headers=headers)

            if r.status_code != 200 or r.text == "User token not found" or r.text =="Service not authorized" :
                raise AuthorizationFailure(r.text)
            response = r.text.decode()
            info = json.loads(response)
            my_token = TokenModel()
            my_token.expires = info["access"]["token"]["expires"]
            my_token.id = info["access"]["token"]["id"]
            my_token.tenant = info["access"]["token"]["tenant"]
            return my_token
        elif auth_api == 'v3':
            headers = {ACCEPT_HEADER: JSON_TYPE, X_AUTH_TOKEN_HEADER: admin_token, X_SUBJECT_TOKEN_HEADER: token}
            r = self.client.get(url +"/" + TOKENS_PATH_V3, headers=headers)
            response = r.text.decode()
            if r.status_code is not 200:
                raise AuthorizationFailure(response)
            info = json.loads(response)
            my_token = TokenModel()
            my_token.expires = info["token"]["expires_at"]
            my_token.id = token
            my_token.tenant = info["token"]["project"]
            return my_token

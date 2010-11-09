#!/usr/bin/env python


import urllib
import httplib
import base64
import json


DEF_API_VERSION = '1.0'


class RightScaleClientException(Exception):
    def __init__(self, response):
        """
        @param response: HTTP response object.
        @type response: httplib.HTTPResponse
        """
        self.response = response

    def __str__(self):
        return '%s:%s' % (response.status, response.reason)


class RightScaleClient:
    """
    RightScale API client.  Takes care of the basic authentication
    header, the request, reply, etc.  Provides CRUD primitives for
    RightScale resources.
    """
    def __init__(self, account, username, password):
        """
        @param account: RightScale account identifier.
        @type account: types.IntType
        @param username: RightScale username.
        @type username: types.StringType
        @param password: RightScale password.
        @type username: types.StringType
        """
        self.account = account
        self.username = username
        self.password = password
        self.__base64_cred = base64.encodestring('%s:%s' % (username, password))[:-1]
        self.__connection = httplib.HTTPSConnection('my.rightscale.com')

    def request(self, method, resource, params={}):
        """
        @param method: HTTP method ('GET', 'POST', 'PUT', or 'DELETE').
        @type method: types.StringType
        @param resource: RightScale resource (eg, 'servers').
        @type resource: types.StringType
        @param params: Key/value pairs to be used in the query string.
        @type params: types.DictType
        @return: HTTP response object
        """
        if method not in ('GET', 'POST', 'PUT', 'DELETE'):
            raise ValueError, 'Unsupported method: %s' % method
        if not params.has_key('api_version'):
            params['api_version'] = DEF_API_VERSION
        if not params.has_key('format'):
            params['format'] = 'js'
        headers = {
            'X-API-VERSION' : params['api_version'],
            'Authorization' : 'Basic %s' % self.__base64_cred,
        }
        url = '/api/acct/%s/%s' % (self.account, resource)
        params = urllib.urlencode(params)
        if method == 'GET':
            url += '?' + params
            self.__connection.request(method, url, headers=headers)
        elif method in ('POST', 'PUT'):
            self.__connection.request(method, url, params, headers)
        elif method == 'DELETE':
            self.__connection.request(method, url, headers=headers)
        else:
            raise ValueError, 'Unsupported method: %s' % method
        return self.__connection.getresponse()

    def get(self, resource, params={}):
        """
        @param resource: RightScale resource (eg, 'servers').
        @type resource: types.StringType
        @param params: Key/value pairs to be used in the query string.
        @type params: types.DictType
        @return: HTTP response object, which may contain a JSON/XML body.
        @rtype: httplib.HTTPResponse
        """
        return self.request('GET', resource, params)

    def post(self, resource, params={}):
        """
        @param resource: RightScale resource (eg, 'servers').
        @type resource: types.StringType
        @param params: Key/value pairs to be used in the query string.
        @type params: types.DictType
        @return: Location (href) of the new resource.
        @rtype: types.StringType
        """
        response = self.request('POST', resource, params)
        location = response.getheader('location', '')
        if not location:
            raise RightScaleClientException(response)
        return location

    def put(self, resource, params={}):
        """
        @param resource: RightScale resource (eg, 'servers').
        @type resource: types.StringType
        @param params: Key/value pairs to be used in the query string.
        @type params: types.DictType
        @return: Success or failure.
        @rtype: types.BooleanType
        """
        response = self.request('PUT', resource, params)
        if response.status not in (200, 204):
            raise RightScaleClientException(response)
        return True

    def delete(self, resource):
        """
        @param resource: RightScale resource (eg, 'servers').
        @type resource: types.StringType
        @return: Success or failure.
        @rtype: types.BooleanType
        """
        response = self.request('DELETE', resource)
        if response.status not in (200, 204):
            raise RightScaleClientException(response)
        return True


class RightScale:
    """
    Top-level abstraction of a RightScale account.
    """
    def __init__(self, account, username, password):
        self.__client = RightScaleClient(account, username, password)

    def __get_deployments(self):
        response = self.__client.get('deployments')
        deployments = json.loads(response.read())
        return deployments

    def __get_servers(self):
        response = self.__client.get('servers')
        servers = json.loads(response.read())
        return servers

    def __get_server_templates(self):
        response = self.__client.get('server_templates')
        server_templates = json.loads(response.read())
        return server_templates

    deployments = property(__get_deployments)
    servers = property(__get_servers)
    server_templates = property(__get_server_templates)


if __name__ == '__main__':
    import json
    from optparse import OptionParser
    from getpass import getpass
    from pprint import pprint

    opt_parser = OptionParser()
    opt_parser.add_option(
        '-p', '--password',
        dest='password',
        action='store', type='string',
        help='RightScale password')
    opt_parser.add_option(
        '-u', '--username',
        dest='username',
        action='store', type='string',
        help='RightScale username')
    opt_parser.add_option(
        '-a', '--account',
        dest='account',
        action='store', type='int',
        help='RightScale account ID')
    opt_parser.add_option(
        '-v', '--verbose',
        dest='verbose',
        action='store_true', default=False,
        help='Enable verbose output')
    opts, args = opt_parser.parse_args()

    # If we do not have the username, prompt for it
    if opts.username:
        username = opts.username
    else:
        username = raw_input('RightScale Username: ')

    # If we do not have the password, prompt for it
    if opts.password:
        password = opts.password
    else:
        password = getpass('RightScale Password: ')

    # If we do not have the account ID, prompt for it
    if opts.account:
        account = opts.account
    else:
        account = raw_input('RightScale Account ID: ')

    rightscale = RightScale(account, username, password)
    print rightscale.servers

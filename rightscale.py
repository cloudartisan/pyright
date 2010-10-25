#!/usr/bin/env python


import urllib2
import base64
import json


def build_request(account_id, username, password, resource):
    base64_cred = base64.encodestring('%s:%s' % (username, password))[:-1]  
    headers = {
        'X-API-VERSION' : '1.0',
        'Authorization' : 'Basic %s' % base64_cred,
    }
    # Get all server templates
    url = 'https://my.rightscale.com/api/acct/%s/%s?api_version=1.0&format=js' % (account_id, resource)
    return urllib2.Request(url, headers=headers)


def handle_rightscript_request(account_id, username, password, resource):
    request = build_request(account_id, username, password, resource)
    try:
        response = urllib2.urlopen(request)
        json_content = json.loads(response.read())
    except urllib2.HTTPError, response:
        logging.error('Response error code (%s)' % response.code)
        json_content = {}
    except urllib2.URLError, error_response:
        logging.error('Request failure (%s)' % response.reason)
        json_content = {}
    return json_content


def get_all_server_templates(account_id, username, password):
    return handle_rightscript_request(account_id, username, password, 'server_templates')


def get_all_servers(account_id, username, password):
    return handle_rightscript_request(account_id, username, password, 'servers')

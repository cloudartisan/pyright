#!/usr/bin/env python


import urllib2
import base64
import json
from optparse import OptionParser
from getpass import getpass

from rightscale import get_all_servers, get_all_server_templates


def parse_args():
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
        dest='account_id',
        action='store', type='int',
        help='RightScale account ID')
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
    if opts.account_id:
        account_id = opts.account_id
    else:
        account_id = raw_input('RightScale Account ID: ')
    return account_id, username, password


def main():
    account_id, username, password = parse_args()
    all_server_templates = get_all_server_templates(account_id, username, password)
    all_servers = get_all_servers(account_id, username, password)

    # Determine all the server templates used by servers
    all_server_template_hrefs_used = []
    for server in all_servers:
        all_server_template_hrefs_used.append(server['server_template_href'])

    # Determine all the orphaned server templates
    orphaned_server_templates = []
    for server_template in all_server_templates:
        if server_template['href'] not in all_server_template_hrefs_used:
            orphaned_server_templates.append(server_template)

    # Display all the orphaned server templates
    for server_template in orphaned_server_templates:
        print '%s|%s' % (server_template['nickname'], server_template['href'])


if __name__ == '__main__':
    main()

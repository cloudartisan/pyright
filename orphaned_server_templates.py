#!/usr/bin/env python


import urllib2
import base64
import json
from optparse import OptionParser
from getpass import getpass
from pprint import pprint

from rightscale import RightScale


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
    return account, username, password, opts.verbose


def main():
    account, username, password, verbose = parse_args()
    rightscale = RightScale(account, username, password)
    all_server_templates = rightscale.server_templates
    all_servers = rightscale.servers

    # Determine all the server templates used by servers
    all_server_template_hrefs_used = []
    for server in all_servers:
        all_server_template_hrefs_used.append(server['server_template_href'])

    # Determine all the orphaned server templates
    orphaned_server_templates = []
    for server_template in all_server_templates:
        if not server_template['is_head_version']:
            continue
        if server_template['href'] not in all_server_template_hrefs_used:
            orphaned_server_templates.append(server_template)

    # Display all the orphaned server templates
    for server_template in orphaned_server_templates:
        if verbose:
            pprint(server_template)
            print
        else:
            print server_template['href']


if __name__ == '__main__':
    main()

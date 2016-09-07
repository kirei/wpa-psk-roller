#!/usr/bin/env python3
#
# Copyright (c) 2016, Kirei AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""WPA(2)-PSK Roller"""

import argparse
import datetime
import json
import os
import random
import sys
import tempfile
import yaml
from pexpect import pxssh


CONFIG_FILE = 'wpa_psk_roller.yaml'


def configure_psk(config: dict, psk: str, debug: bool=False):
    """Configure WLC with PSK"""

    ssid_profile = config['ssid_profile']

    host_prompt = "({})".format(config['shortname'])
    user_prompt = host_prompt +' >'
    enable_prompt = host_prompt + ' #'
    config_prompt = host_prompt + ' (config) #'
    ssid_prompt = host_prompt + ' (SSID Profile "{}") #'.format(ssid_profile)

    session = pxssh.pxssh(encoding='utf8', timeout=10)

    if debug:
        session.logfile = sys.stdout

    session.force_password = True
    session.login(server=config['hostname'],
                  username=config['username'],
                  password=config['password'],
                  auto_prompt_reset=False)

    # enable
    session.expect_exact(user_prompt)
    session.sendline('enable')
    session.expect_exact('Password:')
    session.sendline(config['enable_password'])

    # configure PSK
    session.expect_exact(enable_prompt)
    session.sendline('configure terminal')
    session.expect_exact(config_prompt)
    session.sendline('wlan ssid-profile "{}"'.format(ssid_profile))
    session.expect_exact(ssid_prompt)
    session.sendline('wpa-passphrase "{}"'.format(psk))
    session.expect_exact(ssid_prompt)
    session.sendline('end')

    # save configuration
    session.expect_exact(enable_prompt)
    session.sendline('write memory')

    # finish
    session.expect_exact(enable_prompt, timeout=60)
    session.sendline('exit')
    session.logout()


def publish_psk(psk: str, output_filename: str, output_format: str):
    """Publish PSK"""
    dirname = os.path.dirname(output_filename)
    pskfile = tempfile.NamedTemporaryFile(mode='w', delete=False, dir=dirname)
    if output_format == 'json':
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        data = {'psk': psk, 'timestamp': timestamp}
        json.dump(data, pskfile)
    elif output_format == 'text':
        print(psk, file=pskfile)
    pskfile.close()
    os.rename(pskfile.name, output_filename)


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description='WPA(2)-PSK Roller')
    parser.add_argument('--config',
                        default=CONFIG_FILE,
                        metavar='filename',
                        help='Configuration file')
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Enable debugging')
    args = parser.parse_args()

    try:
        config_stream = open(args.config, "r")
        config_data = yaml.load(config_stream)
    except:
        print('Failed to read configuration file {}'.format(args.config), file=sys.stderr)
        exit(1)

    try:
        wordlist_1 = config_data['wordlist']['first']
        wordlist_2 = config_data['wordlist']['second']
    except KeyError:
        print('Wordlist not correctly configured')
        exit(1)

    word_1 = random.choice(wordlist_1).lower()
    word_2 = random.choice(wordlist_2).lower()
    psk = word_1 + '-' + word_2

    try:
        configure_psk(config_data['wlc'], psk, debug=args.debug)
    except Exception as ex:
        print('Error configuring PSK with WLC', file=sys.stderr)
        if args.debug:
            print(ex, file=sys.stderr)
        exit(1)

    filename = config_data['publish']['filename']
    try:
        output_format = config_data['publish']['format']
    except KeyError:
        output_format = 'json'
    try:
        publish_psk(psk, filename, output_format)
    except Exception as ex:
        print('Error publishing PSK in {}'.format(filename), file=sys.stderr)
        if args.debug:
            print(ex, file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
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
import sys
import json
import datetime
import os
import tempfile
import random
import yaml
from pexpect import pxssh
#import pprint

CONFIG_FILE = 'wpa_psk_roller.yaml'


def configure_psk(config, psk):
    """Configure WLC with PSK"""
    session = pxssh.pxssh()
    session.force_password = True
    session.login(config['hostname'], config['username'], config['password'])
    session.expect(['pattern'])
    session.sendline('config terminal')
    session.expect(['pattern'])
    session.sendline('wlan ssid-profile "{}"'.format(config['ssid_profile']))
    session.expect(['pattern'])
    session.sendline('wpa-passphrase "{}"'.format(psk))
    session.expect(['pattern'])
    session.sendline('end')
    session.sendline('write memory')
    session.expect(['pattern'])
    session.logout()


def publish_psk(psk, output_filename, output_format):
    """Publish PSK"""
    dirname = os.path.dirname(output_filename)
    pskfile = tempfile.NamedTemporaryFile(mode='w', delete=False, dir=dirname)
    if output_format=='json':
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        data = {'psk': psk, 'timestamp': timestamp}
        json.dump(data, pskfile)
    elif output_format=='text':
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
        print('Failed to read configuration file {}'.format(CONFIG_FILE), file=sys.stderr)
        exit(1)

    wordlist_1 = config_data['wordlist']['first']
    wordlist_2 = config_data['wordlist']['second']

    word_1 = random.choice(wordlist_1).lower()
    word_2 = random.choice(wordlist_2).lower()
    psk = word_1 + '-' + word_2

    try:
        configure_psk(config_data['wlc'], psk)
    except Exception as ex:
        print('Error configuring PSK with WLC', file=sys.stderr)
        if args.debug:
            print(ex, file=sys.stderr)
        exit(1)

    filename = config_data['publish']['filename']
    try:
        output_format = config_data['publish']['format']
    except:
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

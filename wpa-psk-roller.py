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

import sys
import yaml
import json
import datetime
import os
import tempfile
from pexpect import pxssh
import random
import pprint

CONFIG_FILE = 'wpa-psk-roller.yaml'


def configure_psk(config, psk):
    """Configure WLC with PSK"""
    # session = pxssh.pxssh()
    # session.force_password = True
    # session.login(config['hostname'], config['username'], config['password'])
    # session.sendline('config terminal')
    # session.sendline('wlan ssid-profile "{}"'.format(config['ssid_profile']))
    # session.sendline('wpa-passphrase "{}"'.format(psk))
    # session.sendline('end')
    # session.sendline('write memory')
    # session.logout()


def publish_psk(config, psk):
    """Publish PSK"""
    file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {'psk': psk, 'timestamp': timestamp}
    json.dump(data, file)
    file.close()
    os.rename(file.name, config['filename'])


def main():
    """Main function"""

    config_stream = open(CONFIG_FILE, "r")
    config_data = yaml.load(config_stream)

    wordlist_1 = config_data['wordlist']['first']
    wordlist_2 = config_data['wordlist']['second']

    word_1 = random.choice(wordlist_1).lower()
    word_2 = random.choice(wordlist_2).lower()
    psk = word_1 + '-' + word_2

    configure_psk(config_data['wlc'], psk)
    publish_psk(config_data['publish'], psk)


if __name__ == "__main__":
    main()

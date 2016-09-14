#!/usr/bin/env python

from setuptools import setup

setup(
    name='wpa_psk_roller',
    version='0.0',
    description='WPA PSK Roller for ArubaPS',
    author='Kirei AB',
    author_email='info@kirei.se',
    classifiers=['License :: OSI Approved :: BSD License'],
    url='https://github.com/kirei/wpa-psk-rollover',
    scripts=['wpa_psk_roller.py'],
    install_requires=[
        'setuptools',
        'pexpect',
        'pyyaml'
    ]
)

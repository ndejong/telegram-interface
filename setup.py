#!/usr/bin/env python3

from setuptools import setup, find_packages
from telegram_interface_cli import NAME
from telegram_interface_cli import VERSION

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name=NAME.replace('_','-'),
    version=VERSION,
    description='A quick tool for listing the Telegram Messenger groups that a user is within.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='telegram telegram-group',

    author='Nicholas de Jong',
    author_email='contact@nicholasdejong.com',
    url='https://github.com/ndejong/telegram-interface',
    license='BSD 2-Clause',

    packages=find_packages(),
    scripts=['bin/telegram-interface'],

    install_requires=['argparse', 'telethon'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

)

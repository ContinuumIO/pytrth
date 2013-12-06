#!/usr/bin/env python

from setuptools import setup

setup(name='pytrth',
    packages=['trth', 'trth.scripts'],
    version='1.1',
    description='Python interface to the Thomson Reuters Tick History API.',
    author=['James Brotchie', 'Francesc Alted'],
    author_email=['brotchie@gmail.com', 'francesc@continuum.io'],
    url='https://github.com/brotchie/pytrth',
    install_requires=['suds', 'pyyaml', 'pandas', 'pyftpdlib'],
    entry_points={
        'console_scripts' : [
            'ftp_handler = trth.scripts.ftp_handler:main',
            'ftp_push = trth.scripts.ftp_push:main',
            'pytrth = trth.scripts.pytrth:main',
        ]
    }
)
